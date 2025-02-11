import configparser
from typing import List, Union, Optional

from numpy import ndarray

from verdictnet.config import root_path, get_config
from verdictnet.models.node import Node


class Embedding:
    def __init__(self, conf: Optional[configparser.ConfigParser] = None):
        from sentence_transformers import SentenceTransformer

        self.conf = conf or get_config()
        # Load a pre-trained model
        self.model = SentenceTransformer(
            self.conf.get('embedding', 'model_name_or_path'),
            cache_folder=self.conf.get('embedding', 'cache')
        )

    def embed_nodes(self, nodes: List[Node]) -> tuple[
        List[Union[List, ndarray]],
        List[str],
        List[dict]
    ]:
        texts = [node.render() for node in nodes]

        # Generate embeddings
        embeddings = self.model.encode(texts)
        documents = [node.render() for node in nodes]
        metadata = [
            {
                'level': node.level,
                'uuid': node.uuid,
                # 'parent_uuid': node.parent.uuid,
                # 'child_uuids': [child.uuid for child in node.children],
                'data-uuid': node.uuid,
                'id': node.id,
                'content': node.content
            } for node in nodes
        ]

        return embeddings, documents, metadata

    def embed_string(self, text: str):
        return self.model.encode(text).tolist()
