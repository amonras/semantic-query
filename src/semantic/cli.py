"""
Command line interface for the semantic package.

Commands:
- Parse: Parse a PDF file and generate a ParsedDocument object (to be stored or printed).
- Load: Load a ParsedDocument object from a file into the vector database
- Query: Query the vector database for similar documents
- Respond: Generate a response to a query based on the query and a set of retrieved documents
"""
from semantic.parser import parse


def init_parser():
    import argparse

    cli_parser = argparse.ArgumentParser(description="Command line interface for the semantic query package.")
    subparsers = cli_parser.add_subparsers(dest="command", help="Available commands")

    # Parse command
    parse_parser = subparsers.add_parser("parse", help="Parse a PDF file and generate a ParsedDocument object")
    parse_parser.add_argument("-f", "--file", required=True, help="Path to the PDF file to parse")
    parse_parser.add_argument("-o", "--output", help="Path to save the parsed document JSON")

    # Load command
    load_parser = subparsers.add_parser("load",
                                        help="Load a ParsedDocument object from a file into the vector database")
    load_parser.add_argument("-f", "--file", required=True, help="Path to the ParsedDocument JSON file")

    # Query command
    query_parser = subparsers.add_parser("query", help="Query the vector database for similar documents")
    query_parser.add_argument("-q", "--query", required=True, help="Query text for database search")

    # Respond command
    respond_parser = subparsers.add_parser("respond",
                                           help="Generate a response to a query based on retrieved documents")
    respond_parser.add_argument("-q", "--query", required=True, help="Query text for response generation")

    return cli_parser


def main():
    parser = init_parser()
    args = parser.parse_args()

    if args.command == "parse":
        parse(args.file, args.output)
    elif args.command == "load":
        raise NotImplementedError("Load command not implemented")
    elif args.command == "query":
        raise NotImplementedError("Query command not implemented")
    elif args.command == "respond":
        raise NotImplementedError("Respond command not implemented")
    else:
        parser.print_help()
        exit(1)
