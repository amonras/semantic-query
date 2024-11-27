from typing import List, Union, Tuple

from numpy import ndarray
from sentence_transformers import SentenceTransformer
from torch import Tensor

from models.node import Node


class Embedding:
    def __init__(self):
        # Load a pre-trained model
        self.model = SentenceTransformer(  # Lightweight, fast model
            'all-MiniLM-L6-v2',
            cache_folder='../cache/',
        )

    def embed_nodes(self, nodes: List[Node]) -> Tuple[
        List[Union[List[Tensor], ndarray, Tensor]],
        List[str],
        List[dict]
    ]:
        texts = [node.render() for node in nodes]

        # Generate embeddings
        embeddings = self.model.encode(texts)
        documents = [node.render() for node in nodes]
        metadata = [{'content': node.content} for node in nodes]

        return embeddings, documents, metadata

    def embed_string(self, text: str) -> Tensor:
        return self.model.encode(text)
