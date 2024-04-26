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





dag2 = DAG(
    dag_id="KB_scrape",
    schedule_interval="0 1 * * *",  # Daily at 1 am
    start_date=days_ago(1),
    catchup=False,
    dagrun_timeout=timedelta(minutes=60),
    tags=["pdf scraping", "Pinecone", "Law Docs"],
)

with dag2:

    download_files_S3_task = PythonOperator(
        task_id='Download_from_s3' ,
        python_callable=download_pdf,
    )

    KB_pdf_scraping_task = PythonOperator(
        task_id='Knowledge_base_scraping',
        python_callable=scrape_pdf,
    )

    upload_KB_task = PythonOperator(
        task_id='Upload_to_pinecone',
        python_callable=upload_pinecone
    )

    download_files_S3_task >> KB_pdf_scraping_task >> upload_KB_task # type: ignore