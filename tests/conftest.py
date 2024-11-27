from pathlib import Path

from pytest import fixture

resources = Path(__file__).parent / "resources"


@fixture
def html_text():
    with open(resources / "codigo_civil.html") as f:
        return f.read()
