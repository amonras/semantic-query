import os
from pathlib import Path

from bs4 import BeautifulSoup
import requests
import re


def scrape_website(url, target):
    """
    Download all the pdf links recursively from the given website
    and save them in the "pdfs" folder.
    :param url:
    :return:
    """
    # Download the webpage
    response = requests.get(url)
    target = Path(target)
    soup = BeautifulSoup(response.text, "html.parser")

    # Find all the pdf links
    pdf_links = soup.find_all("a", href=re.compile(pattern=r"\.pdf$"))

    # Create the pdfs folder if it doesn't exist
    if not os.path.exists(target / "pdfs"):
        os.makedirs(target / "pdfs")

    # Download the pdfs
    for link in pdf_links:
        pdf_url = link["href"]
        pdf_name = pdf_url.split("/")[-1]
        pdf_path = os.path.join(target / "/pdfs", pdf_name)

        # Download the pdf
        pdf_response = requests.get(pdf_url)
        with open(pdf_path, "wb") as f:
            f.write(pdf_response.content)

        print(f"Downloaded {pdf_name}")

        # Download the pdfs recursively
        scrape_website(pdf_url)


if __name__ == "__main__":
    scrape_website(
        url="https://seu.castellarvalles.cat/arxivador/index.php/s/9ob0VSaRD20Sq9r",
        target="../docs"
    )