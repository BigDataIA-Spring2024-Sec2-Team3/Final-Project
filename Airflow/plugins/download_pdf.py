# Filename: download_pdf.py (to be placed in the Airflow plugins folder)
import boto3
from dotenv import load_dotenv
import os
from io import BytesIO
from PyPDF2 import PdfReader
import json
load_dotenv(override=True)


def download_pdf():
    bucket_name = os.getenv('AWS_BUCKET_NAME')
    download_path = os.getenv('AIRFLOW_FILES_PATH')
    # download_path = '/Users/ldy/git/dokcer_airflow/Airflow/files'
    ak = os.getenv("AWS_SK")
    aki = os.getenv("AWS_AK")
    if download_path is not None:
        if not os.path.exists(download_path):
            os.makedirs(download_path)
    else:
        print('No file path in the docke image')
        exit(1)

    # Initialize a session using Amazon S3 credentials
    session = boto3.Session(
        aws_access_key_id=aki,
        aws_secret_access_key=ak,
        region_name='us-east-1'
    )
    s3 = session.resource('s3')

    local_directory_path = download_path

    bucket = s3.Bucket(bucket_name)

    # Iterate over the objects in the bucket
    for obj in bucket.objects.all():
        if obj.key.endswith('.pdf'):
            # Define the local file path to save the PDF
            local_file_path = os.path.join(local_directory_path, obj.key)
            # Create any directories included in the object key
            os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
            # Download the file
            bucket.download_file(obj.key, local_file_path)
            print(f"Downloaded {obj.key} to {local_file_path}")
