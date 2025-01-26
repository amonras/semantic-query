import configparser
from typing import Optional, List

from verdictnet import config
from verdictnet.models.node import Node
from verdictnet.storage.chroma_storage import ChromaStorage
from verdictnet.storage.graph_storage import GraphStorage


class HybridStorage:
    def __init__(self, chroma_storage: ChromaStorage, graph_storage: GraphStorage):
        """
        Initialize HybridStorage with ChromaStorage and GraphStorage instances.
        """
        self.chroma_storage: ChromaStorage = chroma_storage
        self.graph_storage: GraphStorage = graph_storage

    def store(self, root_node: Node):
        """
        Store a Node hierarchy in both ChromaDB and Neo4j.
        """
        # Store in Neo4j
        self.graph_storage.store(root_node)

        # Flatten the hierarchy for ChromaDB
        all_nodes = self.flatten_hierarchy(root_node)

        # Store in ChromaDB
        self.chroma_storage.store_batch(all_nodes)

    def flatten_hierarchy(self, root_node: Node) -> List[Node]:
        """
        Flatten a Node hierarchy into a list of all nodes.
        """
        flat_list = [root_node]
        for child in root_node.children:
            flat_list.extend(self.flatten_hierarchy(child))
        return flat_list

    def query(self, query_string: str, n_results: Optional[int] = None):
        """
        Perform a verdictnet search in ChromaDB and return the results.
        """
        return self.chroma_storage.query(query_string, n_results)

    def delete_all(self):
        """
        Delete all data from both ChromaDB and Neo4j.
        """
        self.chroma_storage.delete_collection(self.chroma_storage.collection_name)
        self.graph_storage.delete_all()

    def retrieve_parent(self, uuid: str) -> Node:
        """
        Retrieve the parent of a node.
        """
        return self.graph_storage.retrieve_parent(uuid)

    def retrieve_hierarchy(self, root_uuid: str) -> Node:
        """
        Retrieve a node and all its children as a hierarchy.

        Args:
            root_uuid (str): The UUID of the root node to retrieve.

        Returns:
            Node: The root node with all its children populated.
        """
        return self.graph_storage.retrieve_hierarchy(root_uuid)

    @classmethod
    def get_hybrid_storage(cls, conf: Optional[configparser.ConfigParser] = None) -> 'HybridStorage':
        conf = conf or config.get_config()

        chroma_storage = ChromaStorage.get_chroma_storage(conf)
        graph_storage = GraphStorage.get_graph_storage(conf)

        return cls(chroma_storage, graph_storage)