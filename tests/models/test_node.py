import json
import tempfile
import webbrowser

from _pytest.fixtures import fixture
from bs4 import BeautifulSoup


from verdictnet.models.node import Node


@fixture
def static_files():
    from verdictnet.config import root_path
    return root_path() / "frontend/static/css"


@fixture
def css_code(static_files):
    with open(static_files / 'document_tree.css', 'r') as css_file:
        yield css_file.read()


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

    def test_save(self):
        node = Node(level="1", content="Test Node")
        with tempfile.NamedTemporaryFile('w', delete=False, suffix='.json') as f:
            path = f.name
        node.save(path)

        with open(path, 'r', encoding='utf8') as file:
            data = json.load(file)

        assert data['level'] == "1"
        assert data['content'] == "Test Node"
        assert 'uuid' in data

    def test_load(self):
        node_data = {
            "id": 1,
            "uuid": "1234",
            "level": "1",
            "content": "Test Node",
            "children": []
        }
        with tempfile.NamedTemporaryFile('w', delete=False, suffix='.json') as f:
            path = f.name
            json.dump(node_data, f)

        loaded_node = Node.load(path)

        assert loaded_node.level == "1"
        assert loaded_node.content == "Test Node"
        assert loaded_node.uuid == "1234"
        assert loaded_node.children == []

    def test_save_with_children(self):
        child_node = Node(level="2", content="Child Node")
        parent_node = Node(level="1", content="Parent Node", children=[child_node])

        with tempfile.NamedTemporaryFile('w', delete=False, suffix='.json') as f:
            path = f.name
        parent_node.save(path)

        with open(path, 'r', encoding='utf8') as file:
            data = json.load(file)

        assert data['level'] == "1"
        assert data['content'] == "Parent Node"
        assert 'uuid' in data
        assert len(data['children']) == 1
        assert data['children'][0]['level'] == "2"
        assert data['children'][0]['content'] == "Child Node"
        assert 'uuid' in data['children'][0]

    def test_load_with_children(self):
        node_data = {
            "id": 1,
            "uuid": "1234",
            "level": "1",
            "content": "Parent Node",
            "children": [
                {
                    "id": 2,
                    "uuid": "5678",
                    "level": "2",
                    "content": "Child Node",
                    "children": []
                }
            ]
        }

        with tempfile.NamedTemporaryFile('w', delete=False, suffix='.json') as f:
            path = f.name
            json.dump(node_data, f)

        loaded_node = Node.load(path)

        assert loaded_node.level == "1"
        assert loaded_node.content == "Parent Node"
        assert loaded_node.uuid == "1234"
        assert len(loaded_node.children) == 1
        assert loaded_node.children[0].level == "2"
        assert loaded_node.children[0].content == "Child Node"
        assert loaded_node.children[0].uuid == "5678"
        assert loaded_node.children[0].children == []
