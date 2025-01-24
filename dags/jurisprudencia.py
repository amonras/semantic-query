from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from datetime import datetime, timedelta
import requests
import json
import os

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
dag = DAG(
    'query_poderjudicial',
    default_args=default_args,
    description='Query www.poderjudicial.es and store results in JSON',
    schedule_interval='@weekly',
    catchup=True,
)

# Define the Python function to query the API and save results
def query_poderjudicial(ds, **kwargs):
    date_from = (datetime.strptime(ds, '%Y-%m-%d') - timedelta(days=7)).strftime('%Y-%m-%d')
    date_to = ds
    #
    # url = 'https://www.poderjudicial.es/search/search.action'
    # payload = {
    #     "action": "query",
    #     "sort": "IN_FECHARESOLUCION:decreasing",
    #     "recordsPerPage": "10",
    #     "databasematch": "AN",
    #     "start": "1",
    #     "FECHARESOLUCIONDESDE": date_from,
    #     "FECHARESOLUCIONHASTA": date_to,
    #     "TIPOINTERES_ACTUAL": "Actualidad",
    #     "TIPOORGANOPUB": "|11|12|13|14|15|16|"
    # }
    # headers = {
    #     'Content-Type': 'application/json'
    # }
    #
    # response = requests.post(url, json=payload, headers=headers)
    # response.raise_for_status()
    #
    # results = response.json()
    # output_path = f'/path/to/output/results_{date_from}_to_{date_to}.json'
    #
    # with open(output_path, 'w') as f:
    #     json.dump(results, f)

# Define the task
query_task = PythonOperator(
    task_id='query_poderjudicial_task',
    provide_context=True,
    python_callable=query_poderjudicial,
    dag=dag,
)

# Set the task in the DAG
query_task
