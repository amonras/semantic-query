import json
import tempfile
import time
from datetime import datetime, timedelta
from functools import wraps

import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from ingestion.parsers.pdf_parser import extract_paragraphs
from ingestion.paths import raw_path, refined_path, fsspec_walk
from config import get_config, logging, get_fs
from models.node import Node
from storage import get_storage

logger = logging.getLogger(__name__)

conf = get_config()
fs = get_fs()

# Base URL for the requests
BASE_URL = "https://www.poderjudicial.es"

# Headers to simulate a browser
HEADERS = {
    "Accept": "text/html, */*; q=0.01",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-GB,en;q=0.5",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Content-Length": "164",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Host": "www.poderjudicial.es",
    "Origin": "https://www.poderjudicial.es",
    "Pragma": "no-cache",
    "Priority": "u=0",
    "Referer": "https://www.poderjudicial.es/search/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:132.0) Gecko/20100101 Firefox/132.0",
    "X-Requested-With": "XMLHttpRequest"
}


def date_range_decorator(func):
    """
    Turns a function that accepts a `date` parameter into a function that
    accepts `start_date` and `end_date` kwargs and iterates `date=` over the range of dates.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_date = kwargs.get('start_date')
        end_date = kwargs.get('end_date')

        if start_date and end_date:
            kwargs.pop('start_date')
            kwargs.pop('end_date')
            for current_date in pd.date_range(start=start_date, end=end_date):
                func(*args, date=current_date, **kwargs)
        else:
            func(*args, **kwargs)

    return wrapper


def create_session():
    """Create and return a requests session with default headers and initialized cookies."""
    session = requests.Session()

    headers_dict = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-GB,en;q=0.5",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Host": "www.poderjudicial.es",
        "Pragma": "no-cache",
        "Priority": "u=0, i",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:132.0) Gecko/20100101 Firefox/132.0"
    }

    response = session.get(f"{BASE_URL}/search/", headers=headers_dict)

    if response.status_code != 200:
        logger.error(f"Failed to create session: {response.content}")
        raise Exception(f"Failed to create session: {response.status_code}")
    logger.debug("Cookies retrieved successfully: ", session.cookies)
    logger.info("Session created successfully.")
    session.headers.update(HEADERS)
    return session


def parse_response(html_text):
    """Parse the response content using BeautifulSoup."""
    soup = BeautifulSoup(html_text, "html.parser")
    return soup


@date_range_decorator
def get_item_pagination(date: datetime, batches=50, force=False):
    """
    Make a request and download all the results pages for a given date range.

    batches: Number of results per page
    force: If True, the function will reprocess the files even if they already exist.
    """

    # TODO: Raise exception if number of results exceeds 200, or implement a finer interval

    data = {
        "action": "query",
        "sort": "IN_FECHARESOLUCION:decreasing",
        "recordsPerPage": str(batches),
        "databasematch": "TS",
        "maxresults": "100",
        "FECHARESOLUCIONDESDE": date.strftime("%d/%m/%Y"),
        "FECHARESOLUCIONHASTA": date.strftime("%d/%m/%Y")
    }

    session = create_session()
    logger.info("Requesting Jurisprudencia for day %s", date.date())
    for page, start in enumerate(range(1, 200, int(data['recordsPerPage'])), 1):
        logger.debug("Retrieving elements %s-%s", start, start + int(data['recordsPerPage']))

        data['start'] = start
        request = requests.Request('POST', f"{BASE_URL}/search/search.action", data=data, headers=HEADERS)
        prepared = session.prepare_request(request)

        logger.debug("Requested %s", request.url)
        logger.debug("Request headers: %s", request.headers)

        response = session.send(prepared)
        response.raise_for_status()

        html_file = raw_path() + f"jurisprudencia/paginations/{date.strftime("%Y/%m/%d")}/response_{page}.html"
        with fs.open(html_file, 'w') as file:
            file.write(response.text)

        # Check if response contains results. If not, abort the loop
        soup = parse_response(response.text)
        numhits = soup.find('div', {'class': 'numhits'})
        if not numhits or not numhits.text:
            logger.debug("No more results found in page %s. Stopping", page)
            break

    logger.info("Finished processing date %s with %s pages", date.date(), str(page))


@date_range_decorator
def refine_item_pagination(date: datetime, force=False):
    """
    Refine the results of the pagination results for a given day,
    extracting reference and metadata for all matches on a given date.

    If `force` is True, the function will reprocess the files even if they already exist.
    """
    refined_file = refined_path() + f'jurisprudencia/paginations/{date.strftime("%Y/%m/%d")}/records.json'
    if fs.exists(refined_file) and not force:
        logger.info("Refined records file already exists for date %s. Skipping", date.date())
        return

    logger.info("Refining date %s", date.date())

    date_path = raw_path() + f"jurisprudencia/paginations/{date.strftime("%Y/%m/%d")}"
    logger.debug(f"Scanning: {date_path}")

    results = []

    for dirpath, dirnames, filenames in fsspec_walk(date_path):
        for filename in filenames:
            if not filename.endswith('.html'):
                continue
            logger.debug(f"  Processing {filename}")
            with fs.open(f"{dirpath}/{filename}", 'r') as file:
                content = file.read()

                soup = parse_response(content)

                page_results = []
                for search_result in soup.findAll('div', {'class': 'searchresult'}):
                    result = search_result.find_all('a', limit=2)[-1].attrs
                    metadatos = search_result.find(attrs={'class': 'metadatos'})
                    result['metadatos'] = [l for l in metadatos.text.split("\n") if l]
                    page_results.append(result)

            logger.debug(f"Found %s results in file %s", len(page_results), filename)
            results.extend(page_results)
            time.sleep(2)

        with fs.open(refined_file, 'w') as file:
            json.dump(results, file, indent=4)

    logger.info("Finished refining date %s with %s records", date.date(), len(results))


@date_range_decorator
def download_pdfs(date: datetime, force=False):
    """
    Download the PDFs referenced in the records file for a given date.

    If `force` is True, the function will reprocess the files even if they already exist.
    """
    # load refined records file
    refined_file = refined_path() + f'jurisprudencia/paginations/{date.strftime("%Y/%m/%d")}/records.json'
    try:
        with fs.open(refined_file, mode='r') as file:
            records = json.load(file)
    except FileNotFoundError:
        logger.warning(f"File not found: {refined_file}")
        records = []

    for record in tqdm(records):
        reference, optimize = record['href'].split("/")[-2:]

        pdf_url = f'{BASE_URL}/search/contenidos.action'

        params = {
            'action': 'accessToPDF',
            'publicinterface': 'true',
            'tab': 'TS',
            'reference': reference,
            'encode': 'true',
            'optimize': optimize,
            'databasematch': 'TS'
        }

        pdf_filename = raw_path() + f'jurisprudencia/pdfs/{date.strftime("%Y/%m/%d")}/{reference}.pdf'
        if fs.exists(pdf_filename) and not force:
            logger.info("PDF file %s.pdf already exists. Skipping", reference)
            continue

        pdf_response = requests.get(pdf_url, params=params)
        pdf_response.raise_for_status()

        with fs.open(pdf_filename, 'wb') as file:
            file.write(pdf_response.content)

        time.sleep(2)


@date_range_decorator
def parse_pdfs(date: datetime, force=False) -> None:
    """
    Parse the PDFs referenced in the records file for a given date. Produce Node objects and store their JSON representation

    If `force` is True, the function will reprocess the files even if they already exist.
    """
    # load refined records file
    refined_file = refined_path() + f'jurisprudencia/paginations/{date.strftime("%Y/%m/%d")}/records.json'
    try:
        with fs.open(refined_file, mode='r') as file:
            records = json.load(file)
    except FileNotFoundError:
        logger.warning(f"File not found: {refined_file}")
        records = []

    for record in tqdm(records):
        reference, optimize = record['href'].split("/")[-2:]

        pdf_filename = raw_path() + f'jurisprudencia/pdfs/{date.strftime("%Y/%m/%d")}/{reference}.pdf'
        parsed_file = refined_path() + f'jurisprudencia/docs/{date.strftime("%Y/%m/%d")}/{reference}.json'
        if fs.exists(parsed_file) and not force:
            logger.info("Parsed file %s.json already exists. Skipping", reference)
            continue

        logger.debug(f"  Processing {pdf_filename}")

        with fs.open(pdf_filename, 'rb') as file:
            content = file.read()

        # Store file into tempfile for pdf parsing
        with tempfile.NamedTemporaryFile() as temp:
            temp.write(content)
            content = extract_paragraphs(temp.file)
            with fs.open(parsed_file, 'w') as file:
                json.dump(content.json(), file, indent=4)


@date_range_decorator
def ingest_pdfs(date: datetime, force=False):
    """ Embed the parsed PDFs into the database """
    storage = get_storage()

    path = refined_path() + f'jurisprudencia/docs/{date.strftime("%Y/%m/%d")}'

    nodes = []

    for dirpath, dirnames, filenames in fsspec_walk(path):
        for filename in filenames:
            if not filename.endswith('.json'):
                continue
            logger.debug(f"  Processing {filename}")

            with fs.open(f"{dirpath}/{filename}", 'r') as file:
                node = Node.from_dict(json.load(file))
            nodes.append(node)

    if nodes:
        storage.store(nodes)


if __name__ == "__main__":
    start_date = datetime.today() - timedelta(days=20)
    end_date = datetime.today() - timedelta(days=1)

    # get_item_pagination(start_date=start_date, end_date=end_date)
    refine_item_pagination(start_date=start_date, end_date=end_date)
    download_pdfs(start_date=start_date, end_date=end_date)
    parse_pdfs(start_date=start_date, end_date=end_date)
    ingest_pdfs(start_date=start_date, end_date=end_date)
