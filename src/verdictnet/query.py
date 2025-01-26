import os
import textwrap

from render.plain_text import PlainTextRenderer
from storage.chroma_storage import ChromaStorage
from storage.hybrid_storage import HybridStorage


def query(q_string: str, n_results: int = 3):
    store = HybridStorage.get_hybrid_storage()
    results = store.query(q_string, n_results=n_results)

    nodes = [store.retrieve_parent(uuid) for uuid in results['ids'][0]]

    return nodes


def parser():
    import argparse

    cli_parser = argparse.ArgumentParser(description="Query the Spanish Civil Code.")
    cli_parser.add_argument("--query", type=str, help="The query string.")
    cli_parser.add_argument('--n_results', type=int, default=3, help="Number of results to return.")
    cli_parser.add_argument('--interactive', action='store_true', help="Interactive mode.")

    return cli_parser


def main(q=None, interactive=False, n_results=3):
    if interactive:
        os.system('clear')
        print("Interactive mode. Enter a query string to search the Spanish Civil Code.")
        while True:
            print("========================================================================")
            try:
                query_string = input("Query: ")
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            results = query(query_string, n_results=n_results)
            print("\n")
            print_results(results)
    else:
        results = query(q, n_results=5)
        print_results(results)


def print_results(nodes):
    for node in nodes:
        print(
            "\n".join(textwrap.wrap(
                PlainTextRenderer.render(node)
            ))
        )


if __name__ == "__main__":
    q = "sobre la colocación de pancartas en balcón de ayuntamiento"
    main(q=q, n_results=3)
