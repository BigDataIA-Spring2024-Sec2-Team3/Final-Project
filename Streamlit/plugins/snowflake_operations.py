import snowflake.connector
from dotenv import load_dotenv
import os
import hashlib
import re
import streamlit as st
import pandas as pd
import requests 
import base64

load_dotenv(override=True)

snowflake_user = os.getenv("SNOWFLAKE_USER")
snowflake_password = os.getenv("SNOWFLAKE_PASSWORD")
snowflake_account = os.getenv("SNOWFLAKE_ACCOUNT")
snowflake_database = os.getenv("SNOWFLAKE_DATABASE")
snowflake_schema = os.getenv("SNOWFLAKE_SCHEMA")

def connect_to_snowflake():
    conn = None
    cursor = None
    try:
        conn = snowflake.connector.connect(
            user=snowflake_user,
            password=snowflake_password,
            account=snowflake_account,
            database=snowflake_database,
            schema=snowflake_schema
        )
        cursor = conn.cursor()
    except Exception as e:
        st.error(f"An error occurred while connecting to Snowflake: {e}")
    return conn, cursor

def register_new_user(username, password, full_name, email):
    conn, cursor = connect_to_snowflake()
    try:
        if conn is None or cursor is None:
            return False, "Failed to connect to the database."
        
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return False, "Invalid email address"

        if len(password) < 8:
            return False, "Password must be at least 8 characters long"

        if not re.match(r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]+$", password):
            return False, "Password must contain at least one letter, one number, and one special character"

        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute(f"INSERT INTO users_project (username, password, full_name, email) VALUES ('{username}', '{hashed_password}', '{full_name}', '{email}')")
        conn.commit()
        return True, "Sign-up successful! Please proceed to login."
        
    except Exception as e:
        return False, f"An error occurred: {e}"
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def validate_user_credentials(username, password):
    conn, cursor = connect_to_snowflake()
    try:
        if conn and cursor:
            cursor.execute(f"SELECT user_id, password FROM users_project WHERE username = '{username}'")
            result = cursor.fetchone()
            if result:
                user_id, stored_password = result
                hashed_password = hashlib.sha256(password.encode()).hexdigest()
                if hashed_password == stored_password:
                    return True, user_id
        return False, None
    except Exception as e:
        st.error(f"An error occurred: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    return False, None


@st.cache_data
def fetch_heatmap_crime_data(input_str):
    try:
        with st.spinner("Loading"):

            if input_str == 'Days of Week':
                table = 'HEATMAP_DOW'
            elif input_str == 'Time of Day':
                table = 'HEATMAP_TOD_GAP'
            elif input_str == 'Holidays':
                table = 'HEATMAP_PUBLICHOLIDAYS'
            elif input_str == 'Year':
                table = 'HEATMAP_YEARLY'
            elif input_str == 'Category':
                table = 'HEATMAP_CAT'
            link = f"http://fastapi:8075/snowflake-heatmap-data/?table={table}"

            response = requests.get(link)
            data = response.json()['data']
            
            if data:
                df = pd.DataFrame(data, columns=['Column0','Crimes','latitude', 'longitude'])
                df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
                df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')

                # grouped_df = df.groupby(by=['latitude', 'longitude']).size().reset_index(name='count') #type: ignore 
                unique_elements = df['Column0'].unique()


                correct_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday','Morning','Afternoon','Evening','Late Night']
                if input_str in [ 'Days of Week', 'Time of Day','Holidays'] :
                    unique_elements = pd.Categorical(unique_elements, categories=correct_order, ordered=True)
                    unique_elements = unique_elements.sort_values()
                if input_str == 'Year':
                    unique_elements.sort()

                df['size'] = df['Crimes'].apply(lambda x: x * 10)  # Scale factor example
                return df,unique_elements
            else:
                st.write("No data available.")
    except Exception as e:
        st.error(f"An error occurred while fetching crime data: {e}")