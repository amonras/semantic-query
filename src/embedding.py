from typing import List, Union

from numpy import ndarray
from sentence_transformers import SentenceTransformer
from torch import Tensor

from models.node import Node


class Embedding:
    def __init__(self):
        # Load a pre-trained model
        self.model = SentenceTransformer(  # Lightweight, fast model
            'all-MiniLM-L6-v2',
            cache_folder='../cache/'
        )

    def embed_nodes(self, nodes: List[Node]) -> List[Union[List[Tensor], ndarray, Tensor]]:
        texts = [node.render() for node in nodes]

        # Generate embeddings
        embeddings = self.model.encode(texts)

        return embeddings

    def embed_string(self, text: str) -> Tensor:
        return self.model.encode(text)
