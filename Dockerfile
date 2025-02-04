FROM apache/airflow:2.10.0

# Set the working directory
WORKDIR /app

# Switch to airflow user to run the application
USER airflow

# Copy the requirements file and install dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Set the entrypoint to Airflow
ENTRYPOINT ["airflow"]
