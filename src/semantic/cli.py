import argparse

import query


def main():
    parser = argparse.ArgumentParser(description="CLI for managing data operations")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Download command
    etl_parser = subparsers.add_parser("etl", help="Run data pipelines")
    etl_parser.add_argument("--path", type=str, help="Path where to look for document specs", )
    etl_parser.add_argument("--force", type=str, help="Force download", default=False)
    etl_subparser = etl_parser.add_subparsers(dest="subcommand", help="Subcommands for the ETL pipeline")
    clean = etl_subparser.add_parser("clean", help="Clean data from vector database")
    ingest = etl_subparser.add_parser("run", help="Ingest data into vector database")
    ingest.add_argument("--path", type=str, help="Path where to look for document specs", )

    # Query command
    query_parser = subparsers.add_parser("query", help="Query data")
    query_parser.add_argument("--query", type=str, help="The query string.")
    query_parser.add_argument('--n_results', type=int, default=3, help="Number of results to return.")
    query_parser.add_argument('--interactive', action='store_true', help="Interactive mode.")

    # Server command
    server_parser = subparsers.add_parser("server", help="Run server")
    server_parser.add_argument("-p", "--port", type=int, help="Port to run the frontend on", default=8000)

    args = parser.parse_args()

    if args.command == "etl":
        handle_etl(args)
    elif args.command == "query":
        handle_query(args)
    elif args.command == "server":
        handle_server(args)
    else:
        parser.print_help()


def handle_etl(args):
    import etl
    if args.subcommand == "clean":
        etl.clean()
    elif args.subcommand == "run":
        etl.run(force_download=args.force, path=args.path)
    else:
        print("No {args.subcommand} subcommand found.")


def handle_query(args):
    query.main(q=args.query, interactive=args.interactive, n_results=args.n_results)


def handle_server(args):
    from frontend.server import server
    server.main()


if __name__ == "__main__":
    main()
