from pathlib import Path
from unittest.mock import patch
import pytest
from src.scripts.download import get_docspecs


@pytest.fixture
def mock_os_walk():
    with patch('os.walk') as mock_walk:
        yield mock_walk


def test_get_docspecs_folder(mock_os_walk):
    mock_os_walk.return_value = [
        ('/some/folder', ('subdir',), ('file1.json', 'file2.json')),
    ]
    path = Path('/some/folder')
    result = get_docspecs(path)
    expected = [Path('/some/folder/file1.json'), Path('/some/folder/file2.json')]
    assert result == expected

def test_get_docspecs_file():
    path = Path('/some/folder/file1.json')
    result = get_docspecs(path)
    expected = [Path('/some/folder/file1.json')]
    assert result == expected

def test_get_docspecs_default(mock_os_walk):
    mock_os_walk.return_value = [
        ('/default/path', ('subdir',), ('file1.json', 'file2.json')),
    ]
    result = get_docspecs()
    expected = [Path('/default/path/file1.json'), Path('/default/path/file2.json')]
    assert result == expected