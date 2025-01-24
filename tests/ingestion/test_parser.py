from pytest import fixture
from bs4 import BeautifulSoup

from conftest import codigo_civil_spec
from ingestion.parsers.html_parser import parse


@fixture(scope='class')
def soup(html_text):
    soup = BeautifulSoup(html_text, "html.parser")
    yield soup


class TestParser:
    def test_parse_sequential_siblings(self, soup, codigo_civil_spec):
        tags = soup.findAll('h4')[3:13]
        parsed = parse(tags, docspec=codigo_civil_spec)

        assert len(parsed) == 5
        assert parsed[-1].content == 'CAPÍTULO V: Ámbito de aplicación de los regímenes jurídicos civiles coexistentes en  el territorio nacional'

    def test_parser_advances_tag_head_for_siblings(self, soup, codigo_civil_spec):
        tags = soup.findAll('h4')[3:18]
        parsed = parse(tags, docspec=codigo_civil_spec)

        assert len(parsed) == 5
        # Check we have consumed all tags and the next one is
        assert len(tags) == 5
        assert tags[0].get('class')[0] == 'libro_num'

    def test_parser_returns_when_parent_found(self, soup, codigo_civil_spec):
        tags = soup.findAll(codigo_civil_spec.tags)
        parsed = parse(tags, docspec=codigo_civil_spec, levels=['capitulo'])[:100]

        assert len(parsed) == 5
        assert len(parsed[0].children) == 2

    def test_parse_children(self, soup, codigo_civil_spec):
        tags = soup.findAll('h4')[1:13]
        parsed = parse(tags, docspec=codigo_civil_spec)

        assert len(parsed) == 1
        assert parsed[0].level == 'titulo'
        assert len(parsed[0].children) == 5

    def test_parse_siblings_with_children(self, soup, codigo_civil_spec):
        tags = soup.findAll(['h4', 'h5', 'p'])
        parsed = parse(tags, docspec=codigo_civil_spec, levels=['titulo'])[0]

        assert parsed.level == 'titulo'
        assert parsed.children[0].level == 'capitulo'
        assert parsed.children[0].children[1].level == 'articulo'

    def test_parse_paragraphs(self, soup, codigo_civil_spec):
        tags = soup.findAll(['h4', 'h5', 'p'])
        parsed = parse(tags, docspec=codigo_civil_spec, levels=['document'])

        assert parsed[0].level == 'document'

    def test_parse_entire_doc(self, soup, codigo_civil_spec):
        tags = soup.findAll(codigo_civil_spec.tags)
        parsed = parse(tags, docspec=codigo_civil_spec, levels=['document'])[0]

        assert 'TÍTULO PRELIMINAR' in parsed.children[0].content
        assert 'LIBRO PRIMERO' in parsed.children[1].content
        assert 'TÍTULO I' in parsed.children[1].children[0].content
        assert 'TÍTULO II' in parsed.children[1].children[1].content
        assert 'LIBRO SEGUNDO' in parsed.children[2].content
        assert 'DISPOSICIONES TRANSITORIAS' in parsed.children[4].children[-1].children[4].content
        assert 'DISPOSICIONES ADICIONALES' in parsed.children[4].children[-1].children[5].content
