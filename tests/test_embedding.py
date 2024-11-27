import chromadb
from pytest import fixture

from embedding import Embedding


@fixture
def store_client():
    client = chromadb.Client(
        settings=chromadb.Settings(allow_reset=True)
    )
    yield client
    client.reset()


@fixture
def embedding():
    embedding_engine = Embedding()
    yield embedding_engine


@fixture
def collection(node_capitulo, store_client, embedding):
    collection = store_client.get_or_create_collection(name="test_collection")
    # Embed nodes
    ids = [ch.content for ch in node_capitulo.children]
    embeddings = embedding.embed_nodes(node_capitulo.children)

    collection.add(ids=ids, embeddings=embeddings)

    yield collection
    store_client.delete_collection('test_collection')


class TestEmbedding:
    def test_embed_node(self, node_capitulo, embedding, store_client, collection):
        # Embed nodes
        ids = [ch.content for ch in node_capitulo.children]
        embeddings = embedding.embed_nodes(node_capitulo.children)

        # Store the embeddings
        collection.add(ids=ids, embeddings=embeddings)

    def test_retrieve_node(self, collection, embedding):
        query_embedding = embedding.embed_string("la costumbre")

        retrieved = collection.query(
            query_embeddings=[list(query_embedding.astype(float))],
            n_results=1,
        )

        assert retrieved['ids'][0][0] == 'Artículo 1.'



