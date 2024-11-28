
# NOTE:
This is kept for legacy. 

It contains a first attempt at a semantic query engine, with the pdf upoload functionality. Eventually this will be integrated with the rest of the package but for now we'll do the ingestion offline.

# Semantic Query

A lightweight tool to perform semantic queries on pdf files.

## Installation
    
     pip install -e .

## Usage

    usage: sq [-h] --file FILE --query QUERY
    
    Semantic Query CLI
    
    options:
      -h, --help     show this help message and exit
      --file FILE    Path to the file to be processed
      --query QUERY  Query to be executed

## Server startup
    
    python server.py
