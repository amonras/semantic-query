from argparse import ArgumentParser
from pathlib import Path

from langchain_text_splitters import CharacterTextSplitter

from semantic.consultant import Consultant


def init_parser():
    parser = ArgumentParser(description="Semantic Query CLI")
    parser.add_argument(
        "--file",
        type=str,
        help="Path to the file to be processed",
        required=True
    )
    parser.add_argument(
        '--query',
        type=str,
        help="Query to be executed",
        required=True
    )
    return parser


def main():
    parser = init_parser()
    args = parser.parse_args()

    splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    consultant = Consultant(file=Path(args.file), splitter=splitter)

    docs = consultant.query(args.query)
    for doc in docs:
        print("=================")
        print(doc.page_content)
