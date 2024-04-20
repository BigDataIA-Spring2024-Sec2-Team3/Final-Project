import os
from dotenv import load_dotenv
import logging
from airflow.models import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from datetime import timedelta

load_dotenv(override= True)

dag = DAG(
    dag_id="handle_pdf_dag",
    schedule_interval="0 0 * * *",  # Daily at midnight
    start_date=days_ago(1),
    catchup=False,
    dagrun_timeout=timedelta(minutes=60),
    tags=["pdf_processing", "s3", "snowflake"],
)