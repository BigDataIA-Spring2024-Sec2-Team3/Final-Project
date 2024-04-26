import os
from dotenv import load_dotenv
import logging
from airflow.models import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
from plugins.prapare_data import pulldata
from plugins.upload_snowflake import upload

load_dotenv(override= True)

dag = DAG(
    dag_id="data_pull_dag",
    schedule_interval="10 10 * * *",  # Daily at 10:10 
    start_date=days_ago(1),
    catchup=False,
    dagrun_timeout=timedelta(minutes=60),
    tags=["data processing", "snowflake", "SFdata API"],
)

with dag:

    prepare_data_task = PythonOperator(
        task_id='prepare_data',
        execution_timeout=timedelta(minutes=20), # set timeout for the task
        python_callable=pulldata,
    )    

    upload_snowflkae_task = PythonOperator(
        task_id='upload',
        python_callable=upload,
    )    

    prepare_data_task >> upload_snowflkae_task # type: ignore