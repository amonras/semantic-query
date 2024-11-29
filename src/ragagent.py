import configparser
import logging
from typing import Optional

import chromadb

from query import print_results
from storage import get_storage

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class RAGAgent:
    """
    Holds the state of the RAG application.
    """

    def __init__(self, conf: Optional[configparser.ConfigParser]):
        self.conf = conf
        self.store = get_storage(conf)

    def query(self, query: str) -> chromadb.QueryResult:
        """
        Query the RAG model.
        :param query:
        :return:
        """
        logger.debug(f"Querying RAG model with: {query}")
        responses = self.store.query(q_string=query)
        print_results(responses)

        return responses
