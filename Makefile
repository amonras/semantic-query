.PHONY: setup install start profile server etl test build clean

# Default port for the server
PORT ?= 8000

# Path for ETL documents
ETL_PATH ?= /path/to/docspecs
FORCE ?= true

.PHONY: install
install:
	@echo "Installing requirements..."
	@pip install -r requirements.txt

.PHONY: setup
setup: install
	@echo "Generating .env file with FERNET_KEY..."
	@python3 -c "from cryptography.fernet import Fernet; print(f'FERNET_KEY={Fernet.generate_key().decode()}')" > .env
	@echo ".env file generated."
	@echo "Launching minio..."
	@docker-compose up -d minio
	@echo "Waiting for minio to start..."
	@until docker-compose exec minio mc ready local; do \
		echo "Minio is not healthy yet. Retrying in 5 seconds..."; \
		sleep 5; \
	done
	@echo "Setting up local alias..."
	@docker-compose exec minio mc alias set minio http://localhost:9000 minioadmin minioadmin
	@echo "Creating buckets..."
	@docker-compose exec minio sh -c "mc ls minio/legal || mc mb minio/legal"
	@docker-compose exec minio mc mb minio/airflow-logs
	@echo "Minio setup complete. Stopping minio..."
	@docker-compose stop minio
	@echo "Setup complete."

.PHONY: start
start:
	@echo "Starting up the microservices..."
	@docker-compose up -d

.PHONY: profile
profile:
	@py-spy record -o profile.svg -- python dags/jurisprudencia.py

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