import boto3
import os

BUCKET_NAME = os.getenv("BUCKET_NAME")
AWS_ACCESS_KEY_ID = os.getenv("AWS_AK")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SK")

s3_resource = boto3.resource('s3', 
                             aws_access_key_id=AWS_ACCESS_KEY_ID, 
                             aws_secret_access_key=AWS_SECRET_ACCESS_KEY)


bucket_obj = s3_resource.Bucket(name=BUCKET_NAME)


print(f"Uploading Latest Pulled Incident report to bucket {BUCKET_NAME}")

file_name = "Incident_Reports.csv"


bucket_obj.upload_file(Filename=file_name, Key=file_name)