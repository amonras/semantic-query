import pytest
from unittest.mock import MagicMock, call
from verdictnet.models.node import Node
from verdictnet.storage.transaction_manager import TransactionManager
from verdictnet.storage.hybrid_storage import HybridStorage


@pytest.fixture
def chroma_storage():
    return MagicMock()


@pytest.fixture
def graph_storage():
    return MagicMock()


@pytest.fixture
def hybrid_storage(chroma_storage, graph_storage):
    return HybridStorage(chroma_storage, graph_storage)


@pytest.fixture
def transaction_manager(hybrid_storage):
    return TransactionManager(hybrid_storage)


def test_store_with_transaction_single_node(transaction_manager, hybrid_storage, graph_storage, chroma_storage):
    root_node = Node(uuid="root-uuid", level="root", content="Root Node")

    transaction_manager.store_with_transaction(root_node)

    graph_storage.batch_store.assert_called_once_with([root_node], None)
    chroma_storage.store_batch.assert_called_once_with([root_node])


def test_store_with_transaction_multiple_nodes(transaction_manager, hybrid_storage, graph_storage, chroma_storage):
    root_nodes = [
        Node(uuid="root-uuid-1", level="root", content="Root Node 1"),
        Node(uuid="root-uuid-2", level="root", content="Root Node 2")
    ]

    transaction_manager.store_with_transaction(root_nodes)

    graph_storage.batch_store.assert_called_once_with(root_nodes, None)
    chroma_storage.store_batch.assert_has_calls([
        call([root_nodes[0]]),
        call([root_nodes[1]])
    ])


def test_store_with_transaction_rollback(transaction_manager, hybrid_storage, graph_storage, chroma_storage):
    root_node = Node(uuid="root-uuid", level="root", content="Root Node")

    graph_storage.batch_store.side_effect = Exception("Neo4j error")

    with pytest.raises(RuntimeError, match="Transaction failed: Neo4j error"):
        transaction_manager.store_with_transaction(root_node)

    hybrid_storage.graph_storage.delete_hierarchy.assert_called_once_with(root_node.uuid)
    hybrid_storage.chroma_storage.delete_by_ids.assert_called_once_with([root_node.uuid])


def test_rollback(transaction_manager, hybrid_storage, graph_storage, chroma_storage):
    root_node = Node(uuid="root-uuid", level="root", content="Root Node")

    transaction_manager.rollback(root_node)

    hybrid_storage.graph_storage.delete_hierarchy.assert_called_once_with(root_node.uuid)
    hybrid_storage.chroma_storage.delete_by_ids.assert_called_once_with([root_node.uuid])