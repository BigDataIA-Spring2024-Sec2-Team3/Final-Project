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
from plugins.Law_PDF_Scrapping import scrape_pdf
from plugins.Pinecone_Upsert import upload_pinecone
from plugins.download_pdf import download_pdf





dag1 = DAG(
    dag_id="data_pull_dag",
    schedule_interval="10 10 * * *",  # Daily at 10:10 
    start_date=days_ago(1),
    catchup=False,
    dagrun_timeout=timedelta(minutes=60),
    tags=["data processing", "snowflake", "SFdata API"],
)

with dag1:
    prepare_data_task = PythonOperator(
        task_id='prepare_data',
        execution_timeout=timedelta(minutes=20),  
        python_callable=pulldata,
    )    

    upload_snowflake_task = PythonOperator(
        task_id='Upload_to_snowflake',
        python_callable=upload,
    )    

    prepare_data_task >> upload_snowflake_task # type: ignore

