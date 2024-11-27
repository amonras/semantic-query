import tempfile
import webbrowser

from bs4 import BeautifulSoup

from conftest import static_files


class TestNode:
    def test_render(self, node_titulo):
        text = node_titulo.render()
        assert "      2. Carecerán de validez las disposiciones que  contradigan otra de rango superior." in text

    def test_html(self, node_titulo):
        html = node_titulo.html()
        css_path = static_files / 'document_tree.css'

        # Read the CSS file content
        with open(css_path, 'r') as css_file:
            css_content = css_file.read()

        # Insert the CSS link into the HTML content
        html_with_css = f'<html><head><style>{css_content}</style></head><body>{html}</body></html>'

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

