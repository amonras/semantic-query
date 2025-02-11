import json

from pytest import fixture

from conftest import resources
from verdictnet.ingestion.documentspec import DocumentSpec


@fixture
def document_spec_json():
    with open(resources / "codigo-civil-spec.json", "r") as file:
        yield json.load(file)


class TestDocumentSpec:
    def test_document_spec(self, document_spec_json):
        spec = DocumentSpec.from_dict(document_spec_json)
        assert spec.name == "Código Civil"
        assert spec.url == "url-that-will-never-point-anywhere-as-test-resources-should"
        assert len(spec.schema) == 11
