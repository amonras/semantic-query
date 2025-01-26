import configparser
import logging
from typing import Optional, List

import chromadb

from models.node import Node
from query import print_results
from storage.hybrid_storage import HybridStorage

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class RAGAgent:
    """
    Holds the state of the RAG application.
    """

    def __init__(self, conf: Optional[configparser.ConfigParser]):
        self.conf = conf
        self.store = HybridStorage.get_hybrid_storage(conf)

    def query(self, query: str) -> List[Node]:
        """
        Query the RAG model.
        :param query:
        :return:
        """
        logger.debug(f"Querying RAG model with: {query}")

        responses = self.store.query(query_string=query)

        nodes = [self.store.retrieve_parent(uuid) for uuid in responses['ids'][0]]
        print_results(nodes)

        return nodes
