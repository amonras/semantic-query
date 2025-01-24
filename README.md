# Semantic Graph Search Project

This project is a semantic graph search system designed to manage and query data.
Currently, the interface is a simple command-line interface (CLI) tool and a web server.
The system supports data ingestion, cleaning, querying, and running a server for frontend interactions.


## Quick Start
You should be able to kickstart the project by launching the docker compose setup:
```sh
  $ docker-compose up
```

These are the relevant web interfaces:
- [Frontend: `http://localhost:8000`](http://localhost:8000)
- [ChromaDB Browser: `http://localhost:3000/collections/legal-database`](http://localhost:3000/collections/legal-database)
- [Neo4J Browser: `http://localhost:7474`](http://localhost:7474)
- [Airflow: `http://localhost:8080`](http://localhost:8080)
- [Minio Console: `http://localhost:9001`](http://localhost:9001)


## Functionality

The CLI tool provides the following commands:

### ETL (Extract, Transform, Load)

Run data pipelines to ingest and process documents.

#### Usage:
```sh
$ semantic etl [--path PATH] [--force FORCE] {clean,run}

--path PATH: Path where to look for document specs.
--force FORCE: Force download of documents.
Subcommands:  
clean: Clean data from the vector database.
run: Ingest data into the vector database.
```

### Query
Query the data stored in the system.
Usage:
```sh
    $ semantic query [--query QUERY] [--n_results N_RESULTS] [--interactive]
```
### Server
Run the server to provide a frontend interface.
Usage:
```sh
    $ semantic server [-p PORT]
    
    -p, --port PORT: Port to run the frontend on (default: 8000).
```

## Example usage
```sh
# Clean the vector database
semantic etl clean

# Run the ETL pipeline
semantic etl run --path /path/to/docspecs --force true

# Query the data
semantic query --query "example query" --n_results 5

# Run the server
semantic server --port 8080
```

## Configuration

The `config.ini` file contains the configuration options.

## Main To Do's
- Determine article references and implement the reference graph in a neo4j database.
- Implement an Airflow pipeline to automate the ETL process.
- Implement a deployment mechanism.
- Fine-tune the language model with the knowledge base.
- Implement a context-based response system.
- Ingest "Jurisprudence" documents.

### Longer term:
- Measure ambiguity within the retrieved documents and formulate optimal reply queries to disambiguate.