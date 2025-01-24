import tempfile
import webbrowser

from bs4 import BeautifulSoup


class TestNode:
    def test_render(self, node_titulo):
        text = node_titulo.render()
        assert "      2. Carecerán de validez las disposiciones que  contradigan otra de rango superior." in text

    def test_html(self, node_titulo, css_code):
        html = node_titulo.html()

        # Insert the CSS link into the HTML content
        html_with_css = f'<html><head><style>{css_code}</style></head><body>{html}</body></html>'

        # open html_text in a browser to see the result
        with tempfile.NamedTemporaryFile('w', delete=False, suffix='.html') as f:
            url = 'file://' + f.name
            f.write(html_with_css)

        # ensure html is correctly formatted
        try:
            assert BeautifulSoup(html_with_css, 'html.parser')
        except Exception as e:
            webbrowser.open(url)
            raise e

