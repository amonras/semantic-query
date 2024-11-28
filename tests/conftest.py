from pathlib import Path

from _pytest.fixtures import fixture
from bs4 import BeautifulSoup
from pytest import fixture

from ingestion.documentspec import DocumentSpec
from ingestion.parser import parse

static_files = Path(__file__).parent.parent / "src/semantic_pdf/static/css"
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

