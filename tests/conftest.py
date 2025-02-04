import configparser
from pathlib import Path
from unittest.mock import patch

from bs4 import BeautifulSoup
from pytest import fixture


@fixture(autouse=True)
def mock_config():
    def mock_get_config():
        config = configparser.ConfigParser()
        config.read('resources/config.ini')
        return config

    with patch('verdictnet.config.get_config', mock_get_config):
        yield


from verdictnet.ingestion.documentspec import DocumentSpec
from verdictnet.ingestion.parsers.html_parser import parse

resources = Path(__file__).parent / "resources"


@fixture
def codigo_civil_spec():
    docspec = DocumentSpec.load(resources / "codigo-civil-spec.json")
    yield docspec


@fixture(scope='session')
def html_text():
    with open(resources / "codigo-civil.html") as f:
        yield f.read()


@fixture
def node_titulo(html_text, codigo_civil_spec):
    soup = BeautifulSoup(html_text, "html.parser")
    tags = soup.findAll(codigo_civil_spec.tags)
    parsed = parse(tags, docspec=codigo_civil_spec, levels=['titulo'])[0]

    yield parsed


@fixture
def node_capitulo(html_text, codigo_civil_spec):
    soup = BeautifulSoup(html_text, "html.parser")
    tags = soup.findAll(codigo_civil_spec.tags)
    parsed = parse(tags, docspec=codigo_civil_spec, levels=['capitulo'])[0]

    yield parsed

