import snowflake.connector
from dotenv import load_dotenv
import os
import hashlib
import re
import streamlit as st
import pandas as pd
import requests 


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

def register_new_user(username, password, full_name, email, role):
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
        cursor.execute(f"INSERT INTO users_project (username, password, full_name, email, role) VALUES ('{username}', '{hashed_password}', '{full_name}', '{email}', '{role}')")
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
            cursor.execute(f"SELECT user_id, password, role FROM users_project WHERE username = '{username}'")
            result = cursor.fetchone()
            if result:
                user_id, stored_password, user_role = result
                hashed_password = hashlib.sha256(password.encode()).hexdigest()
                if hashed_password == stored_password:
                    return True, user_id, user_role
        return False, None, None
    except Exception as e:
        st.error(f"An error occurred: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    return False, None, None

def fetch_crime_data():
    try:
        with st.spinner("Loading"):
            response = requests.get("http://fastapi2:8075/snowflake-data")
            data = response.json()['data']
            
            if data:
                df = pd.DataFrame(data, columns=['Column0','latitude', 'longitude', 'year'])
                df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
                df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')

                grouped_df = df.groupby(by=['latitude', 'longitude']).size().reset_index(name='count') #type: ignore 

                # st.write("Aggregated Locations with Count:")
                # st.write(grouped_df.head())

                grouped_df['size'] = grouped_df['count'].apply(lambda x: x * 10)  # Scale factor example

                return grouped_df
            else:
                st.write("No data available.")
    except Exception as e:
        st.error(f"An error occurred while fetching crime data: {e}")
