import os
from configparser import ConfigParser
from pathlib import Path
from typing import List

import requests
from slugify import slugify
from bs4 import BeautifulSoup

from verdictnet.config import get_config, root_path, logging, get_fs
from verdictnet.ingestion.documentspec import DocumentSpec
from verdictnet.ingestion.paths import refined_path, raw_path, html_path
from verdictnet.models.node import Node
from verdictnet.ingestion.parsers.html_parser import parse
from verdictnet.storage.hybrid_storage import HybridStorage
from verdictnet.storage.transaction_manager import TransactionManager

logger = logging.getLogger(__name__)


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
        logger.warning(f"No document Spec files found in provided folder {path}")
    else:
        logger.info(f"Found {len(filenames)} document specs: %s", ",".join([str(f) for f in filenames]))

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
        parsed = [Node(level=docspec.head, content=docspec.name, children=parsed)]
    return parsed


def download_doc(docspec: DocumentSpec, conf, force_download=False):
    """
    Download the document and save it to the raw folder in html format
    """
    fs = get_fs(conf)

    slug_name = slugify(docspec.name)

    target_path = raw_path() + f'{slug_name}.html'

    # Download documents
    if force_download or not os.path.exists(target_path):
        logger.info(f"Downloading document `{docspec.name}`...")
        text = download(docspec)

        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        with fs.open(target_path, 'w') as file:
            file.write(text)


def refine(docspec, conf):
    """
    Take the document in html format and refine it to a json format
    """
    fs = get_fs(conf)

    slug_name = slugify(docspec.name)

    source_filename = f'{slug_name}.html'
    soure_path = raw_path() + source_filename

    with fs.open(soure_path, 'r') as file:
        text = file.read()

    target = refined_path() + f'{slug_name}.json'

    main_node = get_document_structure(text, docspec=docspec)

    main_node[0].save(target)
    logger.info(f"Saved refined in '{target}'.")


def render_html(docspec: DocumentSpec, conf: ConfigParser):
    fs = get_fs(conf)

    slug_name = slugify(docspec.name)
    main_node_path = refined_path() + f'{slug_name}.json'
    main_node = Node.load(main_node_path)

    html_file = html_path() + f'{slug_name}.html'
    with fs.open(html_file, 'w', encoding='utf-8') as file:
        file.write(main_node.html(
            preamble="""
            <html lang="es"><head><meta charset="utf-8" /></head>
            """
        ))
    logger.info(f"HTML saved to '{html_file}'.")


def ingest(docspec: DocumentSpec, conf: ConfigParser):
    slug_name = slugify(docspec.name)
    main_node_path = refined_path() + f'{slug_name}.json'
    main_node = Node.load(main_node_path)

    storage = TransactionManager.get_transaction_manager(conf)
    # all_nodes = main_node.get_all(level=docspec.embed_level)

    storage.store_with_transaction(main_node)


def clean():
    print("This will empty both databases. Are you sure you want to continue? (y/n)")
    response = input()
    if response.lower() != 'y':
        print("Aborted.")
        return

    conf = get_config()

    store = HybridStorage.get_hybrid_storage(conf)
    store.delete_all()
    print(f"Cleared all databases.")


def run(force_download=False, path=None):
    conf = get_config()

    # Load Docspecs
    filenames = get_docspecs(path)
    docspecs = [DocumentSpec.load(filename) for filename in filenames]

    for docspec in docspecs:
        # Download document
        download_doc(docspec, conf, force_download)

        # Refining documents
        refine(docspec, conf)

        # Render html
        render_html(docspec, conf)

        # Ingesting into vector database
        ingest(docspec, conf)


if __name__ == "__main__":
    run()
