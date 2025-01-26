FROM apache/airflow:2.10.0

USER root
COPY requirements.txt .
COPY src/ src/
COPY setup.py .
COPY config.ini .
RUN chown -R airflow src/
RUN apt-get update && apt-get install -y build-essential

# Switch to airflow user to run the application
USER airflow
RUN pip install -r requirements.txt
RUN pip install .