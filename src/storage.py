import configparser
from typing import Optional, List

import chromadb

import config
from embedding import Embedding
from models.node import Node


class Storage:
    def __init__(
            self,
            embedding: Embedding,
            chroma_client: chromadb.Client,
            collection_name: str = 'default',
            conf: Optional[configparser.ConfigParser] = None
    ):
        self.config = conf or config.get_config()
        self.n_results = int(self.config['rag']['n_results'])
        self.client: chromadb.Client = chroma_client
        self.collection_name = collection_name
        self.collection = self.client.get_or_create_collection(name=collection_name)
        self.embedding = embedding

    def delete_collection(self, collection):
        try:
            self.client.get_collection(collection)
            print(f'Deleting all documents in collection {collection}...')
            self.client.delete_collection(name=collection)
        except chromadb.errors.InvalidCollectionException as e:
            pass

    def store(self, nodes: List[Node]):
        print(f'Adding/updating documents to collection {self.collection_name}...')
        collection = self.client.get_or_create_collection(self.collection_name)

        # Embed nodes
        ids = [str(ch.uuid) for ch in nodes]
        embeddings, documents, metadatas = self.embedding.embed_nodes(nodes)

        collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )

    def query(self, q_string: str, n_results: Optional[int] = None) -> chromadb.QueryResult:
        query_embedding = self.embedding.embed_string(q_string)

        retrieved = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results or self.n_results,
        )

        return retrieved

    def get_html_docs(self) -> List[str]:
        self.config['storage']['html']


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
    embedding = Embedding(conf=conf)

    return Storage(embedding=embedding, chroma_client=chroma_client, collection_name=collection)
