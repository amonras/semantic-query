from pathlib import Path

import requests
from bs4 import BeautifulSoup
import json

from parser.parser import parse


def download_civil_code():
    # URL del texto consolidado del Código Civil en el BOE
    url = "https://boe.es/buscar/act.php?id=BOE-A-1889-4763&p=20230301&tn=0"

    # Hacer la solicitud HTTP
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"No se pudo acceder al texto consolidado. Código de estado: {response.status_code}")

    return response.text


def parse_civil_code(text):
    # Parsear el HTML
    soup = BeautifulSoup(text, "html.parser")

    # Extraer el contenido principal
    content_divs = soup.find_all("div", {"id": "textoxslt"})
    if not content_divs:
        raise Exception("No se pudo encontrar el contenido consolidado del Código Civil.")

    return content_divs[0]


def get_document_structure(text):
    soup = BeautifulSoup(text, "html.parser")
    tags = soup.findAll(['h4', 'h5', 'p'])
    return parse(tags, current_tag='anexo')[0]


def save_to_json(data, filename=Path(__file__).parent.parent / "data/codigo_civil.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def main():
    print("Descargando el Código Civil consolidado...")

    text = download_civil_code()

    print("Dividiendo en artículos...")
    articles = get_document_structure(text)
    save_to_json(articles)
    print("Artículos guardados en 'codigo_civil.json'.")


if __name__ == "__main__":
    main()
