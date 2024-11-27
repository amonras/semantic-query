import configparser
from typing import Optional

import chromadb

import config
from embedding import Embedding
from models.node import Node


class Storage:
    def __init__(self, embedding: Embedding, collection: chromadb.Collection):
        self.collection = collection
        self.embedding = embedding

    def store(self, node: Node):
        # Get the strings of all Nodes
        all_nodes = node.get_all(level='articulo')

        # Embed nodes
        ids = [ch.content for ch in all_nodes]
        embeddings = self.embedding.embed_nodes(all_nodes)

        self.collection.add(ids=ids, embeddings=embeddings)

    def query(self, q_string: str) -> chromadb.QueryResult:
        query_embedding = self.embedding.embed_string(q_string)

        retrieved = self.collection.query(
            query_embeddings=[list(query_embedding.astype(float))],
            n_results=1,
        )

        return retrieved


def get_chroma(conf: Optional[configparser.ConfigParser] = None) -> chromadb.Client:
    conf = conf or config.get_config()

    if conf['chroma']['type'] == 'http':
        client = chromadb.HttpClient(
            host=conf['chroma']['host'],
            port=int(conf['chroma']['port']),
        )
    elif conf['chroma']['type'] == 'local':
        client = chromadb.PersistentClient(
            path=str(config.root_path() / conf.get('storage', 'path')),
        )
    else:
        # return in-memory client
        print("WARNING: Using in-memory client. This is ephemeral")
        client = chromadb.EphemeralClient()

    return client


def get_storage(conf: Optional[configparser.ConfigParser] = None) -> Storage:
    conf = conf or config.get_config()

    chroma_client = get_chroma(conf)

    collection = chroma_client.get_or_create_collection(name=conf.get('storage', 'collection'))

    embedding = Embedding()
    return Storage(embedding=embedding, collection=collection)
