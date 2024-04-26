## API to get the data
from fastapi import FastAPI,HTTPException
from fastapi.responses import JSONResponse
import snowflake.connector
from dotenv import load_dotenv
import os
load_dotenv(override=True)


app = FastAPI()

SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")
SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER")
SNOWFLAKE_PASSWORD =  os.getenv("SNOWFLAKE_PASSWORD")
SNOWFLAKE_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE")
SNOWFLAKE_DATABASE = os.getenv("SNOWFLAKE_DATABASE")
SNOWFLAKE_SCHEMA = os.getenv("SNOWFLAKE_SCHEMA")

def connect_to_snowflake():
    conn = snowflake.connector.connect(
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        account=SNOWFLAKE_ACCOUNT,
        database=SNOWFLAKE_DATABASE,
        schema=SNOWFLAKE_SCHEMA
    )
    return conn


@app.get("/snowflake-data/")
async def get_snowflake_data(table:str = 'MAIN_MAP_LASTWEEK_MODEL'):
    try:
        conn = connect_to_snowflake()
        cursor = conn.cursor()
        query = f"SELECT * FROM CRIMES.DBT_PKALANI.{table}"
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return {"data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/snowflake-heatmap-data/")
async def get_snowflake_data(table: str ='HEATMAP_DOW'):
    try:
        conn = connect_to_snowflake()
        cursor = conn.cursor()
        query = f"SELECT * FROM CRIMES.DBT_PKALANI.{table}"
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return {"data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
