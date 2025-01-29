import pytest
import os

from conftest import resources
from verdictnet.models.node import Node
from verdictnet.ingestion.parsers.pdf_parser import extract_paragraphs


@pytest.fixture
def pdf_file_path():
    return os.path.join(resources / 'jurisprudence.pdf')


def test_extract_paragraphs(pdf_file_path):
    document = extract_paragraphs(pdf_file_path)
    assert len(document.children) > 0  # Ensure paragraphs are extracted
    assert isinstance(document, Node)  # Ensure the result is a list
    assert all(isinstance(child, Node) for child in document.children)  # Ensure all items are strings

    # Additional checks can be added based on the expected content of the PDF
    assert document.render().startswith("Roj: STS 5805/2024 - ECLI:ES:TS:2024:5805")