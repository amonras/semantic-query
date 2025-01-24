import pytest

from storage.graph_storage import GraphStorage
from storage.hybrid_storage import HybridStorage


@pytest.fixture
def hybrid_storage(mocker, graph_storage):
    chroma_storage_mock = mocker.Mock()
    return HybridStorage(chroma_storage_mock, graph_storage)


def mock_neo4j_session(mocker, mock_data):
    session_mock = mocker.Mock()
    session_mock.run.return_value.single.return_value = mock_data
    return session_mock
