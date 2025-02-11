import configparser
from typing import Optional, List

from verdictnet.models.node import Node
from verdictnet.storage.hybrid_storage import HybridStorage
from verdictnet.config import logging, get_config

logger = logging.getLogger(__name__)

# TODO: implement unit tests for this class


class TransactionManager:
    def __init__(self, hybrid_storage: HybridStorage):
        """
        Initialize TransactionManager with a HybridStorage instance.
        """
        self.hybrid_storage = hybrid_storage

    def init_dataset(self, name):
        """
        Check if a parent node for the Dataset already exists in the database. If it doesn't, create it. In any case, return
        the uuid so that all further documents of this dataset will be linked to it.
        """

        # Check if the dataset already exists
        query = {
            "level": "dataset",
            "content": name
        }
        dataset_node = self.hybrid_storage.graph_storage.retrieve_by(level='dataset', content=name)

        if dataset_node:
            logger.info("Dataset already exists in the database")
            return dataset_node[0].uuid

        # If it doesn't, create it
        dataset_node = Node(level="dataset", content=name)
        self.store_with_transaction(dataset_node)
        return dataset_node.uuid

    def store_with_transaction(self, root_nodes: Node | List[Node], parent_uuid: Optional[str] = None):
        """
        Store a Node hierarchy in both ChromaDB and Neo4j, ensuring consistency.
        """
        if not isinstance(root_nodes, list):
            root_nodes = [root_nodes]

        try:
            # Store in Neo4j
            logger.info("Storing in Neo4j...")
            self.hybrid_storage.graph_storage.batch_store(root_nodes, parent_uuid)

            # Store in ChromaDB
            logger.info("Storing in ChromaDB...")
            for node in root_nodes:
                # Flatten the hierarchy for ChromaDB
                all_nodes = self.hybrid_storage.flatten_hierarchy(node)

                # Store in ChromaDB
                self.hybrid_storage.chroma_storage.store_batch(all_nodes)

        except Exception as e:
            # Rollback strategy: remove nodes from both systems if one fails
            for node in root_nodes:
                self.rollback(node)
            raise RuntimeError(f"Transaction failed: {e}")


    def rollback(self, root_node: Node):
        """
        Rollback changes made during a failed transaction.
        """
        try:
            # Delete from Neo4j
            self.hybrid_storage.graph_storage.delete_hierarchy(root_node.uuid)

            # Delete from ChromaDB
            all_node_uuids = [node.uuid for node in self.hybrid_storage.flatten_hierarchy(root_node)]
            self.hybrid_storage.chroma_storage.delete_by_ids(all_node_uuids)

        except Exception as rollback_error:
            # Log rollback failure
            logger.error(f"Rollback failed: {rollback_error}")

    @classmethod
    def get_transaction_manager(cls, conf: Optional[configparser.ConfigParser] = None) -> 'TransactionManager':
        conf = conf or get_config()

        # Initialize HybridStorage and TransactionManager
        hybrid_storage = HybridStorage.get_hybrid_storage(conf)
        transaction_manager = TransactionManager(hybrid_storage)
        return transaction_manager
