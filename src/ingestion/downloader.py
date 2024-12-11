import json
import time
import webbrowser
import requests
from bs4 import BeautifulSoup

from config import root_path, get_config

conf = get_config()

# Base URL for the requests
BASE_URL = "https://www.poderjudicial.es"

data = {
    "action": "query",
    "sort": "IN_FECHARESOLUCION:decreasing",
    "recordsPerPage": "50",
    "databasematch": "TS",
    "maxresults": "100",
    "FECHARESOLUCIONDESDE": "01/11/2024",
    "FECHARESOLUCIONHASTA": "05/11/2024"
}

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
        raise Exception(f"Failed to create session: {response.status_code}")
    print("Cookies retrieved successfully: ", session.cookies)
    print("Session created successfully.")
    session.headers.update(HEADERS)
    return session


def parse_response(response):
    """Parse the response content using BeautifulSoup."""
    soup = BeautifulSoup(response.text, "html.parser")
    return soup


if __name__ == "__main__":
    session = create_session()

    results = []

    for page, start in enumerate(range(1, 200, 50), 1):
        print(start)

        data['start'] = start
        request = requests.Request('POST', f"{BASE_URL}/search/search.action", data=data, headers=HEADERS)
        prepared = session.prepare_request(request)

        print(request.url)
        print(request.headers)

        response = session.send(prepared)
        response.raise_for_status()

        html_file = root_path() / conf['storage']['html'] / f"response_{page}.html"
        with open(html_file, 'w') as file:
            file.write(response.text)

        soup = parse_response(response)

        page_results = []
        for search_result in soup.findAll('div', {'class': 'searchresult'}):
            result = search_result.find_all('a', limit=2)[-1].attrs
            metadatos = search_result.find(attrs={'class': 'metadatos'})
            result['metadatos'] = [l for l in metadatos.text.split("\n") if l]
            page_results.append(result)

        if not page_results:
            print(f"No more results found in page {page}. Stopping")
            break

        print(f"Found {len(page_results)} results in page {page}")
        results.extend(page_results)
        time.sleep(2)

    with open(root_path() / conf['storage']['refined'] / 'response.json', 'w') as file:
        json.dump(results, file, indent=4)
