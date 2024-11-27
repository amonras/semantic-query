import configparser
from typing import Optional

import chromadb

import config
from embedding import Embedding
from models.node import Node


class Storage:
    def __init__(self, embedding: Embedding, chroma_client: chromadb.Client, collection_name: str = 'default'):
        self.client: chromadb.Client = chroma_client
        self.collection_name = collection_name
        self.collection = self.client.get_or_create_collection(name=collection_name)
        self.embedding = embedding

    def delete_all(self):
        print('Deleting all documents...')
        self.client.delete_collection(name=self.collection_name)

    def store(self, node: Node):
        print(f'Adding documents to collection `{self.collection_name}`...')
        collection = self.client.get_or_create_collection(name=self.collection_name)

        # Get the strings of all Nodes
        all_nodes = node.get_all(level='articulo')

        # Embed nodes
        ids = [str(ch.id) for ch in all_nodes]
        embeddings, documents, metadatas = self.embedding.embed_nodes(all_nodes)

        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )

    def query(self, q_string: str, n_results: int = 1) -> chromadb.QueryResult:
        query_embedding = self.embedding.embed_string(q_string)

        retrieved = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
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
    collection = conf.get('storage', 'collection')
    embedding = Embedding()

    return Storage(embedding=embedding, chroma_client=chroma_client, collection_name=collection)
