import os
import textwrap

from storage import get_storage


def query(q_string: str, n_results: int = 3):
    store = get_storage()
    results = store.query(q_string, n_results=n_results)

    return results


def parser():
    import argparse

    cli_parser = argparse.ArgumentParser(description="Query the Spanish Civil Code.")
    cli_parser.add_argument("--query", type=str, help="The query string.")
    cli_parser.add_argument('--n_results', type=int, default=3, help="Number of results to return.")
    cli_parser.add_argument('--interactive', action='store_true', help="Interactive mode.")

    return cli_parser


def main():
    args = parser().parse_args()

    if args.interactive:
        os.system('clear')
        print("Interactive mode. Enter a query string to search the Spanish Civil Code.")
        while True:
            print("========================================================================")
            try:
                query_string = input("Query: ")
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            results = query(query_string, n_results=args.n_results)
            print("\n")
            print_results(results)
    else:
        results = query(args.query, n_results=5)
        print_results(results)


def print_results(results):
    for doc in results['documents'][0]:
        print("\n" + doc)


if __name__ == "__main__":
    main()
