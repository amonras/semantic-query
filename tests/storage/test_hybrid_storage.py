import pytest
from unittest.mock import MagicMock
from models.node import Node
from storage.hybrid_storage import HybridStorage


@pytest.fixture
def chroma_storage():
    return MagicMock()


@pytest.fixture
def graph_storage():
    return MagicMock()


@pytest.fixture
def hybrid_storage(chroma_storage, graph_storage):
    return HybridStorage(chroma_storage, graph_storage)


def test_store(hybrid_storage, chroma_storage, graph_storage):
    root_node = Node(uuid="root-uuid", level="root", content="Root Node", children=[
        Node(uuid="child-uuid-1", level="child", content="Child Node 1"),
        Node(uuid="child-uuid-2", level="child", content="Child Node 2")
    ])

    hybrid_storage.store(root_node)

    graph_storage.store.assert_called_once_with(root_node)
    chroma_storage.store_batch.assert_called_once_with([root_node, root_node.children[0], root_node.children[1]])


def test_flatten_hierarchy(hybrid_storage):
    root_node = Node(uuid="root-uuid", level="root", content="Root Node", children=[
        Node(uuid="child-uuid-1", level="child", content="Child Node 1"),
        Node(uuid="child-uuid-2", level="child", content="Child Node 2")
    ])

    flat_list = hybrid_storage.flatten_hierarchy(root_node)

    assert len(flat_list) == 3
    assert flat_list[0].uuid == "root-uuid"
    assert flat_list[1].uuid == "child-uuid-1"
    assert flat_list[2].uuid == "child-uuid-2"


def test_query(hybrid_storage, chroma_storage):
    query_string = "test query"
    hybrid_storage.query(query_string)

    chroma_storage.query.assert_called_once_with(query_string, None)


def test_delete_all(hybrid_storage, chroma_storage, graph_storage):
    hybrid_storage.delete_all()

    chroma_storage.delete_collection.assert_called_once()
    graph_storage.delete_all.assert_called_once()


def test_retrieve_hierarchy(hybrid_storage, graph_storage):
    root_uuid = "root-uuid"
    hybrid_storage.retrieve_hierarchy(root_uuid)

    graph_storage.retrieve_hierarchy.assert_called_once_with(root_uuid)
