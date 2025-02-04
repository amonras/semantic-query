.PHONY: setup install start stop profile server etl test build clean

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
	@if [ ! -f .env ]; then \
		echo "Generating .env file with FERNET_KEY..."; \
		echo "Generating .env file with FERNET_KEY..."; \
		python3 -c "from cryptography.fernet import Fernet; \
		fernet_key = Fernet.generate_key().decode(); \
		template = 'FERNET_KEY={fernet_key}\\nAIRFLOW_UID=50000'; \
		print(template.format(fernet_key=fernet_key)); \
		print('_AIRFLOW_WWW_USER_USERNAME=airflow'); \
		print('_AIRFLOW_WWW_USER_PASSWORD=airflow'); " > .env; \
  		echo ".env file generated."; \
	else \
		echo ".env file already exists. Skipping FERNET_KEY generation."; \
	fi
	@if [ ! -f config/local/.env ]; then \
		echo "Copying .env file to config/local..."; \
		cp .env config/local/; \
		echo ".env file copied."; \
	else \
		echo "config/local/.env file already exists. Skipping config/local copy."; \
	fi
	@echo "Launching minio..."
	@docker-compose up -d minio
	@echo "Waiting for minio to start..."
	@until docker-compose exec minio mc ready local; do \
		echo "Minio is not healthy yet. Retrying in 5 seconds..."; \
		sleep 5; \
	done
	@echo "Setting up local alias..."
	@docker-compose exec minio mc alias set minio http://localhost:9000 minioadmin minioadmin
	@echo "Checking if bucket 'legal' exists..."
	@if ! docker-compose exec minio mc ls minio/legal; then \
  		echo "Creating bucket 'legal'..."; \
  		docker-compose exec minio mc mb minio/legal; \
 	else \
  		echo "Bucket 'legal' already exists. Skipping creation."; \
	fi
	@echo "Checking if bucket 'airflow-logs' exists..."
	@if ! docker-compose exec minio mc ls minio/airflow-logs; then \
  		echo "Creating bucket 'airflow-logs'..."; \
  		docker-compose exec minio mc mb minio/airflow-logs; \
 	else \
  		echo "Bucket 'airflow-logs' already exists. Skipping creation."; \
	fi
	@echo "Minio setup complete. Stopping minio..."
	@docker-compose stop minio
	@echo "Setup complete."

.PHONY: start
start:
	@echo "Detecting virtual environment..."
	@if [ -n "$$VIRTUAL_ENV" ]; then \
		echo "Virtual environment detected at $$VIRTUAL_ENV"; \
		export VIRTUAL_ENV_PATH=$$VIRTUAL_ENV; \
	else \
		echo "No virtual environment detected."; \
	fi
	@echo "Starting up the microservices..."
	@docker-compose up -d
	@echo "Done."
	@echo "\nFrontends are available at the following links:"
	@echo "ChromaDB: http://localhost:3000/collections/legal-database"
	@echo "Neo4j: http://localhost:7474"
	@echo "Minio: http://localhost:9000"
	@echo "Airflow: http://localhost:8080"

.PHONY: stop
stop:
	@echo "Stopping the microservices..."
	@docker-compose down


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