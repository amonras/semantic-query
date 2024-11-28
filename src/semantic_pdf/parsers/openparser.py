import os
from typing import List

from langchain_community.embeddings import HuggingFaceEmbeddings
from openparse import DocumentParser, processing

OPEN_AI_KEY = os.getenv("OPENAI_API_KEY")


class HuggingFaceEmbeder:
    def __init__(self, batch_size=256):
        self.model = HuggingFaceEmbeddings(
            model_name='sentence-transformers/all-MiniLM-l6-v2',
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': False},
            show_progress=True,
        )
        self.batch_size = batch_size

    def embed_many(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts in batches.

        Args:
            texts (list[str]): The list of texts to embed.
            batch_size (int): The number of texts to process in each batch.

        Returns:
            List[List[float]]: A list of embeddings.
        """
        res = []
        for i in range(0, len(texts), self.batch_size):
            batch_texts = texts[i : i + self.batch_size]
            # use the HuggingFaceEmbeddings to embed the batch of texts into a list of CreateEmbeddingResponse
            batch_res = self.model.embed_documents(batch_texts)
            res.extend(batch_res)
        return res


class Parser:
    def __init__(self):
        self.parser = DocumentParser()

    def parse(self, file_path=None):
        processing.semantic_transforms.EmbeddingModel
        semantic_pipeline = processing.SemanticIngestionPipeline(
            openai_api_key=OPEN_AI_KEY,
            model="text-embedding-3-large",
            min_tokens=64,
            max_tokens=1024,
        )
        parser = DocumentParser(
            processing_pipeline=semantic_pipeline,
        )
        parsed_content = parser.parse(file_path)
