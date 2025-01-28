import pendulum
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import timedelta, datetime

# Define the default arguments
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': pendulum.today('UTC').add(days=-8 * 7),  # Start date 8 weeks ago
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


def get_item_pagination_task(date: str):
    from verdictnet.ingestion.downloader import get_item_pagination
    return get_item_pagination(datetime.strptime(date, "%Y-%m-%d"))


def refine_item_pagination_task(date: str):
    from verdictnet.ingestion.downloader import refine_item_pagination
    return refine_item_pagination(datetime.strptime(date, "%Y-%m-%d"))


def download_pdfs_task(date: str):
    from verdictnet.ingestion.downloader import download_pdfs
    return download_pdfs(datetime.strptime(date, "%Y-%m-%d"))


def parse_pdfs_task(date: str):
    from verdictnet.ingestion.downloader import parse_pdfs
    return parse_pdfs(datetime.strptime(date, "%Y-%m-%d"))


def ingest_pdfs_task(date: str):
    from verdictnet.ingestion.downloader import ingest_pdfs
    from verdictnet.storage.transaction_manager import TransactionManager
    from verdictnet.config import get_config

    transaction_manager = TransactionManager.get_transaction_manager(get_config())
    dataset_uuid = transaction_manager.init_dataset("Jurisprudencia")
    return ingest_pdfs(date=datetime.strptime(date, "%Y-%m-%d"),
                transaction_manager=transaction_manager,
                dataset_uuid=dataset_uuid)


# Define the DAG
with DAG(
    'query_poderjudicial',
    default_args=default_args,
    description='Query www.poderjudicial.es and store results in JSON',
    schedule='@daily',
    catchup=True,
):
    item_pagination_task = PythonOperator(
        task_id='get_item_pagination',
        python_callable=get_item_pagination_task,
        op_kwargs={'date': "{{ ds }}"},
    )

    refine_pagination_task = PythonOperator(
        task_id='refine_item_pagination',
        python_callable=refine_item_pagination_task,
        op_kwargs={'date': "{{ ds }}"},
    )

    download_pdfs = PythonOperator(
        task_id='download_pdfs',
        python_callable=download_pdfs_task,
        op_kwargs={'date': "{{ ds }}"},
    )

    parse_pdfs = PythonOperator(
        task_id='parse_pdfs',
        python_callable=parse_pdfs_task,
        op_kwargs={'date': "{{ ds }}"},
    )

    ingest_pdfs = PythonOperator(
        task_id='ingest_pdfs',
        python_callable=ingest_pdfs_task,
        op_kwargs={'date': "{{ ds }}"},
    )

    item_pagination_task >> refine_pagination_task >> download_pdfs >> parse_pdfs >> ingest_pdfs

