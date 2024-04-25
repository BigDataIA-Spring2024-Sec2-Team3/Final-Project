#!/usr/bin/env python
import warnings
warnings.filterwarnings("ignore")
from dotenv import load_dotenv
from sqlalchemy import create_engine
import bcrypt
import os
import csv

load_dotenv()

create_stage = """CREATE OR REPLACE STAGE STAGING DIRECTORY = ( ENABLE = true );"""

create_table_query = """CREATE OR REPLACE TABLE incident_reports (
        incident_datetime TIMESTAMP,
        incident_date TIMESTAMP,
        incident_time STRING,
        incident_year STRING,
        incident_day_of_week STRING,
        report_datetime TIMESTAMP,
        row_id STRING,
        incident_id STRING,
        incident_number STRING,
        report_type_code STRING,
        report_type_description STRING,
        incident_code STRING,
        incident_category STRING,
        incident_subcategory STRING,
        incident_description STRING,
        resolution STRING,
        police_district STRING,
        filed_online STRING,
        cad_number STRING,
        intersection STRING,
        cnn STRING,
        analysis_neighborhood STRING,
        supervisor_district STRING,
        supervisor_district_2012 STRING,
        latitude STRING,
        longitude STRING,
        point STRING
);"""

upload_to_stage = """PUT file:///Users/ldy/git/Final-Project-damg/Airflow/files/Incident_Reports.csv @CRIMES.PROD.STAGING;"""


copy_stage_to_table = """COPY INTO CRIMES.PROD.INCIDENT_REPORTS
        FROM @CRIMES.PROD.STAGING
        FILES = ('Incident_Reports.csv.gz')
        FILE_FORMAT = (
            TYPE=CSV,
            SKIP_HEADER=1,
            FIELD_DELIMITER=',',
            TRIM_SPACE=FALSE,
            FIELD_OPTIONALLY_ENCLOSED_BY='"',
            REPLACE_INVALID_CHARACTERS=TRUE,
            DATE_FORMAT=AUTO,
            TIME_FORMAT=AUTO,
            TIMESTAMP_FORMAT=AUTO
        )
        ON_ERROR=ABORT_STATEMENT;"""


load_dotenv()

u=os.getenv("SNOWFLAKE_USER")
p=os.getenv("SNOWFLAKE_PASSWORD")
ai=os.getenv("SNOWFLAKE_ACCOUNT")

print([u,p,ai])

def upload():
    engine = create_engine(
        'snowflake://{user}:{password}@{account_identifier}/'.format(
            user=u,
            password=p,
            account_identifier=ai,
        )
    )


    try:
        connection = engine.connect()
        connection.execute("USE WAREHOUSE SFCrimes")
        connection.execute("USE DATABASE CRIMES")
        connection.execute("USE SCHEMA PROD")
        
        results = connection.execute(create_stage)
        results = connection.execute(create_table_query)
        results = connection.execute(upload_to_stage)
        results = connection.execute(copy_stage_to_table)

    except Exception as e:
        print(f"Error: {e}")
        
    finally:
        print("Done")
        connection.close() # type: ignore
        engine.dispose() # type: ignore

# upload()