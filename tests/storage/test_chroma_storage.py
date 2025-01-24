import chromadb
import pytest
from unittest.mock import MagicMock
from models.node import Node
from storage.chroma_storage import ChromaStorage
from embedding import Embedding


@pytest.fixture
def chroma_client():
    ClientMock = MagicMock(spec=chromadb.Client)
    client = ClientMock()
    client.get_or_create_collection.return_value = MagicMock()

    yield client


@pytest.fixture
def embedding():
    return MagicMock(spec=Embedding)


@pytest.fixture
def chroma_storage(chroma_client, embedding):
    return ChromaStorage(embedding=embedding, chroma_client=chroma_client, collection_name='test_collection')


def test_store_batch(chroma_storage, chroma_client, embedding):
    nodes = [
        Node(uuid="uuid1", level="level1", content="content1"),
        Node(uuid="uuid2", level="level2", content="content2")
    ]

    embeddings = [[0.1, 0.2], [0.3, 0.4]]
    documents = ["content1", "content2"]
    metadatas = [{"uuid": "uuid1"}, {"uuid": "uuid2"}]

    embedding.embed_nodes.return_value = (embeddings, documents, metadatas)

    chroma_storage.store_batch(nodes)

    chroma_client.get_or_create_collection.assert_called_once_with(name='test_collection')
    chroma_client.get_or_create_collection().upsert.assert_called_once_with(
        ids=["uuid1", "uuid2"],
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas
    )

def test_query(chroma_storage, chroma_client, embedding):
    query_string = "test query"
    query_embedding = [0.1, 0.2]
    embedding.embed_string.return_value = query_embedding

    expected_result = MagicMock(spec=chromadb.QueryResult)
    chroma_client.get_or_create_collection().query.return_value = expected_result

    result = chroma_storage.query(query_string)

    embedding.embed_string.assert_called_once_with(query_string)
    chroma_client.get_or_create_collection().query.assert_called_once_with(
        query_embeddings=[query_embedding],
        n_results=chroma_storage.n_results
    )
    assert result == expected_result

def test_delete_by_ids(chroma_storage, chroma_client):
    ids = ["uuid1", "uuid2"]

    chroma_storage.delete_by_ids(ids)

    chroma_client.get_or_create_collection().delete.assert_called_once_with(ids=ids)

def test_delete_collection(chroma_storage, chroma_client):
    collection_name = "test_collection"

    chroma_storage.delete_collection(collection_name)

    chroma_client.get_collection.assert_called_once_with(collection_name)
    chroma_client.delete_collection.assert_called_once_with(name=collection_name)

def test_delete_collection_invalid_collection(chroma_storage, chroma_client):
    collection_name = "invalid_collection"
    chroma_client.get_collection.side_effect = chromadb.errors.InvalidCollectionException

    chroma_storage.delete_collection(collection_name)

    chroma_client.get_collection.assert_called_once_with(collection_name)
    chroma_client.delete_collection.assert_not_called()