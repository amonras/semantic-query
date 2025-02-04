import pendulum
from airflow import DAG
from airflow.decorators import task_group
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from datetime import timedelta

from slugify import slugify

from verdictnet.config import get_config
from verdictnet.etl import get_docspecs, download_doc, refine, render_html, ingest
from verdictnet.ingestion.documentspec import DocumentSpec

# Define the default arguments
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': pendulum.today('UTC'),  # Start date 8 weeks ago
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


def lazy_download_doc(docspec):
    conf = get_config()
    download_doc(docspec, conf, force_download=False)


def lazy_refine(docspec):
    conf = get_config()
    refine(docspec, conf)


def lazy_render_html(docspec):
    conf = get_config()
    render_html(docspec, conf)


def lazy_ingest(docspec):
    conf = get_config()
    ingest(docspec, conf)


def group(name, docspec):
    """
    Process a specific document
    """
    download_task = PythonOperator(
        task_id=f'download_{name}',
        python_callable=lazy_download_doc,
        op_args=[docspec],
    )

    refine_task = PythonOperator(
        task_id=f'refine_{name}',
        python_callable=lazy_refine,
        op_args=[docspec],
    )

    render_task = PythonOperator(
        task_id=f'render_{name}',
        python_callable=lazy_render_html,
        op_args=[docspec],
    )

    ingest_task = PythonOperator(
        task_id=f'ingest_{name}',
        python_callable=lazy_ingest,
        op_args=[docspec],
    )

    download_task >> refine_task >> render_task >> ingest_task

    return download_task

# Define the DAG
with DAG(
        'download_codigos',
        default_args=default_args,
        description='Download Codigo Civil y Penal',
        schedule="@once",
        catchup=False,
):
    filenames = get_docspecs()
    docspecs = [DocumentSpec.load(filename) for filename in filenames]

    start = EmptyOperator(task_id='start_task')

    for docspec in docspecs:
        name = slugify(docspec.name)

        start >> group(name, docspec)
