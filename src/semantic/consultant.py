import logging
from pathlib import Path
from typing import Optional

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from tika import parser
from langchain_text_splitters import TextSplitter, CharacterTextSplitter

from semantic.splitters.article_splitter import ArticleSplitter

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Consultant:
    def __init__(self, splitter: TextSplitter, file: Optional[Path] = None):
        self.file = file
        self.splitter = splitter or CharacterTextSplitter()

        self.embeddings_model = HuggingFaceEmbeddings(
            model_name='sentence-transformers/all-MiniLM-l6-v2',
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': False},
            show_progress=True,
        )

        self.chroma = Chroma(embedding_function=self.embeddings_model)

        if self.file:
            self.train(self.parse(file, text_splitter=self.splitter))

    def upload_file(self, file: Path):
        logger.debug("Uploading file")
        self.train(self.parse(file, text_splitter=self.splitter))

    def train(self, chunks):
        logger.debug("Training Chroma")
        self.chroma.add_documents(chunks)

    def parse(self, file: Path, text_splitter: TextSplitter) -> list:
        """
        Parse pdf contents using Apache Tika.
        :param file:
        :param text_splitter:
        :return:
        """
        logger.debug("Splitting file into chunks")
        text = parser.from_file(str(file.absolute()))
        chunks = text_splitter.create_documents(texts=[text["content"]])

        return chunks

    def query(self, query: str):
        """
        Query the Chroma database.
        :param query:
        :return:
        """
        docs = self.chroma.similarity_search(query)
        return docs


if __name__ == "__main__":
    my_splitter = ArticleSplitter(title_pattern=r"Art\. \d+ - .*")
    consultant = Consultant(
        file=Path(__file__).parent.parent.parent / "docs/pdfs/sabadell/NNUU_Vol_1_Art.pdf",
        splitter=my_splitter
    )
    query = "Quants metres ha de tenir una vorera perquè sigui accessible?"
    docs = consultant.query(query)
    for doc in docs:
        print(doc.page_content)
