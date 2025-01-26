from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from datetime import datetime, timedelta
import requests
import json
import os

from semantic.ingestion.downloader import get_item_pagination

# Define the default arguments
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(8 * 7),  # Start date 8 weeks ago
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
with DAG(
    'query_poderjudicial',
    default_args=default_args,
    description='Query www.poderjudicial.es and store results in JSON',
    schedule_interval='@daily',
    catchup=True,
):
    item_pagination = PythonOperator(
        task_id='get_item_pagination',
        provide_context=True,
        python_callable=get_item_pagination,
    )
