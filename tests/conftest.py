from pathlib import Path

from bs4 import BeautifulSoup
from pytest import fixture

from parser.parser import parse

static_files = Path(__file__).parent.parent / "src/semantic/static/css"
resources = Path(__file__).parent / "resources"


@fixture
def html_text():
    with open(resources / "codigo_civil.html") as f:
        return f.read()


@fixture
def node_titulo(html_text):
    soup = BeautifulSoup(html_text, "html.parser")
    h4s = soup.findAll(['h4', 'h5', 'p'])
    parsed = parse(h4s, level='titulo_num')[0]

    yield parsed


@fixture
def node_capitulo(html_text):
    soup = BeautifulSoup(html_text, "html.parser")
    h4s = soup.findAll(['h4', 'h5', 'p'])
    parsed = parse(h4s, level='capitulo_num')[0]

    yield parsed