import os
from pathlib import Path
from typing import List

import requests
from bs4 import BeautifulSoup
import json

from config import get_config, root_path
from models.node import Node
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


def get_document_structure(text) -> Node:
    soup = BeautifulSoup(text, "html.parser")
    tags = soup.findAll(['h4', 'h5', 'p'])
    parsed = parse(tags, level='anexo')
    return parsed


def save_to_json(data, filename=Path(__file__).parent.parent / "data/codigo_civil.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def main():
    conf = get_config()
    raw_path = root_path() / conf['storage']['raw'] / 'codigo_civil.html'
    try:
        with open(raw_path, 'r') as file:
            text = file.read()
    except FileNotFoundError:
        print("No se encontró el Código Civil. Descargando...")
        print("Descargando el Código Civil consolidado...")
        text = download_civil_code()

        os.makedirs(os.path.dirname(raw_path), exist_ok=True)
        with open(raw_path, 'w') as file:
            file.write(text)

    print("Dividiendo en artículos...")

    refined_path = root_path() / conf['storage']['refined'] / 'codigo_civil.json'
    main_node = get_document_structure(text)
    os.makedirs(os.path.dirname(refined_path), exist_ok=True)
    main_node.save(refined_path)
    print("Artículos guardados en 'codigo_civil.json'.")

    html_path = root_path() / conf['storage']['html'] / 'codigo_civil.html'
    os.makedirs(os.path.dirname(html_path), exist_ok=True)
    with open(html_path, 'w', encoding='utf-8') as file:
        file.write(main_node.html(
            preamble="""
            <html lang="es"><head><meta charset="utf-8" /></head>
            """
        ))


if __name__ == "__main__":
    main()
