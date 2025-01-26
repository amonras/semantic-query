.PHONY: server etl test build clean

# Default port for the server
PORT ?= 8000

# Path for ETL documents
ETL_PATH ?= /path/to/docspecs
FORCE ?= true

# Docker build
.PHONY: build
build:
	@docker build -t semantic_airflow .

# Run the server
server:
	@echo "Running the server on port $(PORT)..."
	@semantic server --port $(PORT)

# Run the ETL pipeline
etl:
	@echo "Running the ETL pipeline with path $(ETL_PATH) and force $(FORCE)..."
	@semantic etl run --path $(ETL_PATH) --force $(FORCE)

# Run tests
test:
	@echo "Running tests..."
	@pytest

# Clean the vector database
clean:
	@echo "Cleaning the vector database..."
	@semantic etl clean