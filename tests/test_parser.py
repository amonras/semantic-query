from bs4 import BeautifulSoup

from parser.parser import parse


class TestParser:
    def test_parse_sequential_siblings(self, html_text):
        soup = BeautifulSoup(html_text, "html.parser")
        h4s = soup.findAll('h4')[3:13]
        parsed = parse(h4s)

        assert len(parsed) == 5
        assert parsed[-1].content == 'CAPÍTULO V: Ámbito de aplicación de los regímenes jurídicos civiles coexistentes en  el territorio nacional'

    def test_parser_advances_tag_head_for_siblings(self, html_text):
        soup = BeautifulSoup(html_text, "html.parser")
        tags = soup.findAll('h4')[3:18]
        parsed = parse(tags)

        assert len(parsed) == 5
        # Check we have consumed all tags and the next one is
        assert len(tags) == 5
        assert tags[0].get('class')[0] == 'libro_num'

    def test_parser_returns_when_parent_found(self, html_text):
        soup = BeautifulSoup(html_text, "html.parser")
        tags = soup.findAll(['h4', 'h5', 'p'])
        parsed = parse(tags, levels=['capitulo'])[:100]

        assert len(parsed) == 5
        assert len(parsed[0].children) == 2

    def test_parse_children(self, html_text):
        soup = BeautifulSoup(html_text, "html.parser")
        h4s = soup.findAll('h4')[1:13]
        parsed = parse(h4s)

        assert len(parsed) == 1
        assert parsed[0].level == 'titulo'
        assert len(parsed[0].children) == 5

    def test_parse_siblings_with_children(self, html_text):
        soup = BeautifulSoup(html_text, "html.parser")
        h4s = soup.findAll(['h4', 'h5', 'p'])
        parsed = parse(h4s, levels=['titulo'])[0]

        assert parsed.level == 'titulo'
        assert parsed.children[0].level == 'capitulo'
        assert parsed.children[0].children[1].level == 'articulo'

    def test_parse_paragraphs(self, html_text):
        soup = BeautifulSoup(html_text, "html.parser")
        h4s = soup.findAll(['h4', 'h5', 'p'])
        parsed = parse(h4s, levels=['document'])

        assert parsed[0].level == 'document'

    def test_parse_entire_doc(self, html_text):
        soup = BeautifulSoup(html_text, "html.parser")
        tags = soup.findAll(['h4', 'h5', 'p'])
        parsed = parse(tags, levels=['document'])[0]

        assert 'TÍTULO PRELIMINAR' in parsed.children[0].content
        assert 'LIBRO PRIMERO' in parsed.children[1].content
        assert 'TÍTULO I' in parsed.children[1].children[0].content
        assert 'TÍTULO II' in parsed.children[1].children[1].content
        assert 'LIBRO SEGUNDO' in parsed.children[2].content
        assert 'DISPOSICIONES TRANSITORIAS' in parsed.children[4].children[-1].children[4].content
        assert 'DISPOSICIONES ADICIONALES' in parsed.children[4].children[-1].children[5].content