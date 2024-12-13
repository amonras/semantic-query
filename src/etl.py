import os
from pathlib import Path
from typing import List

import requests
from slugify import slugify
from bs4 import BeautifulSoup

from config import get_config, root_path
from ingestion.documentspec import DocumentSpec
from models.node import Node
from ingestion.parsers.html_parser import parse
from storage import get_storage


def get_docspecs(path: Path = None) -> List[Path]:
    """
    Return all the docspecs in the resources folder
    """
    if path is None:
        path = Path(__file__).parent / 'ingestion' / 'resources/'
    filenames = []
    for root, subdirs, files in os.walk(path):
        for file in files:
            if file.endswith('.json'):
                filenames.append(Path(root + '/' + file))

    if not filenames:
        print(f"No document Spec filed found in provided folder {path}")

    return filenames


def get_files(path: Path, extension: str = None, subfolders=False) -> List[Path]:
    """
    Return all the files in the resources folder
    """
    filenames = []
    for root, subdirs, files in os.walk(path):
        for file in files:
            if file.endswith(extension):
                filenames.append(Path(root + '/' + file))
        if not subfolders:
            break

    if not filenames:
        print(f"No files found in provided folder {path}")

    return filenames


def download(docspec: DocumentSpec) -> str:
    # Hacer la solicitud HTTP
    response = requests.get(docspec.url)
    if response.status_code != 200:
        raise Exception(f"No se pudo acceder al texto consolidado. Código de estado: {response.status_code}")

    return response.text


def get_document_structure(text, docspec: DocumentSpec) -> List[Node]:
    soup = BeautifulSoup(text, "html.parser")
    tags = soup.findAll(docspec.tags)
    parsed = parse(tags, docspec=docspec, levels=docspec.wraps or [docspec.head])
    if len(parsed) > 1:
        parsed = [Node(level='root', content=docspec.name, children=parsed)]
    return parsed


def ingest(main_node, docspec: DocumentSpec, store=None):
    # store.delete_collection(docspec.code)

    # Get the strings of all Nodes
    all_nodes = main_node.get_all(level=docspec.embed_level)

    store.store(all_nodes)


def clean():
    conf = get_config()

    collection = conf['storage']['collection']
    store = get_storage()
    store.delete_collection(collection)
    print(f"Deleted collection '{collection}'.")


def run(force_download=False, path=None):
    conf = get_config()

    store = get_storage()

    # Load Docspecs
    filenames = get_docspecs(path)
    docspecs = [DocumentSpec.load(filename) for filename in filenames]

    for docspec in docspecs:

        slug_name = slugify(docspec.name)

        # Download documents
        target_filename = f'{slug_name}.html'
        raw_path = root_path() / conf['storage']['raw'] / target_filename

        if force_download or not os.path.exists(raw_path):
            print(f"Downloading document `{docspec.name}`...")
            text = download(docspec)

            os.makedirs(os.path.dirname(raw_path), exist_ok=True)
            with open(raw_path, 'w') as file:
                file.write(text)
        else:
            with open(raw_path, 'r') as file:
                text = file.read()

        # Refining documents
        target_filename = f'{slug_name}.json'
        refined_path = root_path() / conf['storage']['refined'] / target_filename
        main_node = get_document_structure(text, docspec=docspec)

        os.makedirs(os.path.dirname(refined_path), exist_ok=True)
        main_node[0].save(refined_path)
        print(f"Saved refined in '{target_filename}'.")

        # Saving json
        html_path = root_path() / conf['storage']['html'] / f'{slug_name}.html'
        os.makedirs(os.path.dirname(html_path), exist_ok=True)
        with open(html_path, 'w', encoding='utf-8') as file:
            file.write(main_node[0].html(
                preamble="""
                <html lang="es"><head><meta charset="utf-8" /></head>
                """
            ))
        print(f"HTML saved to '{slug_name}.html'.")

        # Ingesting into vector database
        ingest(main_node[0], docspec, store=store)


if __name__ == "__main__":
    run()
