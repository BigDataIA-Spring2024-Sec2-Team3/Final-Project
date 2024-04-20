import streamlit as st
import snowflake.connector
from dotenv import load_dotenv
import os
import hashlib
import re
import requests

# Load environment variables
load_dotenv(override=True)

# Get Snowflake credentials from environment variables
snowflake_user = os.getenv("SNOWFLAKE_USER")
snowflake_password = os.getenv("SNOWFLAKE_PASSWORD")
snowflake_account = os.getenv("SNOWFLAKE_ACCOUNT")
snowflake_database = os.getenv("SNOWFLAKE_DATABASE")
snowflake_schema = os.getenv("SNOWFLAKE_SCHEMA")

# Function to connect to Snowflake
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

# Streamlit UI
st.set_page_config(
    page_title="Crime Incident Logger",
    page_icon="🚓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(to bottom right, #7F7FD5, #86A8E7, #91EAE4) !important;
    }
    .stButton>button {
        border-radius: 15px !important;
        padding: 8px 16px !important;
        font-size: 16px !important;
        color: #fff !important;
        background-color: #4CAF50 !important;
        border-color: #4CAF50 !important;
        transition: background-color 0.4s ease !important;
    }
    .stButton>button:hover {
        background-color: #45a049 !important;
    }
    .stTextInput>div>div>input {
        border-radius: 15px !important;
        padding: 10px 15px !important;
        font-size: 16px !important;
    }
    .stSelectbox>div>div>div>select {
        border-radius: 15px !important;
        padding: 10px 15px !important;
        font-size: 16px !important;
    }
    .stTextArea>div>textarea {
        border-radius: 15px !important;
        padding: 10px 15px !important;
        font-size: 16px !important;
    }
    .stDateInput>div>input {
        border-radius: 15px !important;
        padding: 10px 15px !important;
        font-size: 16px !important;
    }
    .stTimeInput>div>input {
        border-radius: 15px !important;
        padding: 10px 15px !important;
        font-size: 16px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

INCIDENT_MAPPING = {
    "Recovered Vehicle": ["Recovered Vehicle"],
    "Larceny Theft": ["Larceny - From Vehicle", "Larceny - From Building", "Theft From Vehicle", "Larceny Theft - Bicycle", "Larceny Theft - Purse Snatch", "Larceny Theft - Other", "Larceny Theft - Shoplifting"],
    "Missing Person": ["Missing Person", "Missing Adult"],
    "Other Offenses": ["Non-Criminal", "Other", "Bad Checks", "Arrest", "Miscellaneous Investigation", "Case Closure"],
    "Courtesy Report": ["Courtesy Report"],
    "Disorderly Conduct": ["Disorderly Conduct", "Drunkenness", "Loitering", "Trespass"],
    "Arson": ["Arson"],
    "Robbery": ["Robbery - Street", "Robbery - Carjacking", "Robbery - Commercial", "Robbery - Residential", "Robbery - Other"],
    "Burglary": ["Burglary - Other", "Burglary - Residential", "Burglary - Commercial", "Burglary - Hot Prowl"],
    "Case Closure": ["Case Closure"],
    "Civil Sidewalks": ["Civil Sidewalks"],
    "Prostitution": ["Prostitution"],
    "Drugs": ["Drug Violation", "Drug Offense"],
    "Vandalism": ["Vandalism", "Malicious Mischief"],
    "Traffic Violation": ["Traffic Violation Arrest"],
    "Sex Offense": ["Sex Offense", "Rape", "Rape - Attempted"],
    "Embezzlement": ["Embezzlement"],
    "Fire Report": ["Fire Report"],
    "Weapons Offense": ["Weapons Offense", "Weapons Carrying Etc"],
    "Gambling": ["Gambling"],
    "Forgery And Counterfeiting": ["Forgery And Counterfeiting"],
    "Homicide": ["Homicide"],
    "Human Trafficking": ["Human Trafficking, Commercial Sex Acts", "Human Trafficking (A), Commercial Sex Acts", "Human Trafficking, Involuntary Servitude", "Human Trafficking (B), Involuntary Servitude"],
    "Kidnapping": ["Kidnapping"],
    "Stalking": ["Stalking"],
    "Manslaughter": ["Homicide - Excusable", "Manslaughter"],
    "Suspicious": ["Suspicious Occ", "Suspicious Package"],
    "Trespass": ["Trespass"],
    "Vehicle Impounded": ["Vehicle Impounded"],
    "Fraud": ["Fraud"],
    "Malicious Mischief": ["Malicious Mischief"],
}

POLICE_DISTRICTS = [
    "Out of SF",
    "Central",
    "Bayview",
    "Tenderloin",
    "Mission",
    "Park",
    "Richmond",
    "Southern",
    "Taraval",
    "Ingleside",
    "Northern"
]

# Function to get subcategories based on category
def get_subcategories(category):
    return INCIDENT_MAPPING.get(category, [])

menu_selection = st.sidebar.radio(
    "Go to:",
    ("Login", "Sign Up", "Log Incident", "Crime Data Map" , "Log Out")
)

def register_new_user(username, password, full_name, email):
    conn, cursor = connect_to_snowflake()
    try:
        # Validate email format
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            st.error("Invalid email address")
            return

        # Validate password criteria
        if len(password) < 8:
            st.error("Password must be at least 8 characters long")
            return

        if not re.match(r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]+$", password):
            st.error("Password must contain at least one letter, one number, and one special character")
            return

        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute(f"INSERT INTO users_project (username, password, full_name, email) VALUES ('{username}', '{hashed_password}', '{full_name}', '{email}')")
        conn.commit()
        st.success("Sign-up successful! Please proceed to login.")
    except Exception as e:
        st.error(f"An error occurred: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def validate_user_credentials(username, password):
    conn, cursor = connect_to_snowflake()
    try:
        cursor.execute(f"SELECT user_id, password FROM users_project WHERE username = '{username}'")
        result = cursor.fetchone()
        if result:
            user_id, stored_password = result
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            if hashed_password == stored_password:
                st.session_state.user_id = user_id
                st.success("Login successful!")
                st.session_state.logged_in = True
            else:
                st.error("Incorrect password")
        else:
            st.error("Invalid username")
    except Exception as e:
        st.error(f"An error occurred: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def log_out():
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.success("Logged out successfully!")

def log_incident(date, time, location, incident_category, incident_subcategory, description, police_district):
    conn, cursor = connect_to_snowflake()
    try:
        cursor.execute("""
            INSERT INTO crime_incidents (user_id, date, time, location, incident_category, incident_subcategory, description, police_district) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (st.session_state.user_id, date, time, location, incident_category, incident_subcategory, description, police_district))
        conn.commit()
        st.success("Crime incident logged successfully!")
    except Exception as e:
        st.error(f"An error occurred: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def fetch_crime_data():
    st.write("Outside try")
    try:
        st.write("In try")
        response = requests.get("http://finalproject-fastapi2:8075/snowflake-data")
        data = response.json()
        if data:
            st.write("JSON value for the first row:")
            st.json(data[0])
            locations = [(row[3], row[2]) for row in data]
            st.map(locations)
        else:
            st.write("No data available.")
    except Exception as e:
        st.error(f"An error occurred while fetching crime data: {e}")

if menu_selection == "Login":
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        validate_user_credentials(username, password)
    st.markdown("<hr/>", unsafe_allow_html=True)
    #st.write("Don't have an account? [Sign Up](#Sign-Up)")

elif menu_selection == "Sign Up":
    st.title("Sign Up")
    new_username = st.text_input("New Username")
    new_password = st.text_input("New Password", type="password")
    full_name = st.text_input("Full Name")
    email = st.text_input("Email")
    if st.button("Sign Up"):
        if not new_username or not new_password or not full_name or not email:
            st.error("Please fill in all fields.")
        else:
            register_new_user(new_username, new_password, full_name, email)
    st.markdown("<hr/>", unsafe_allow_html=True)
    #st.write("Already have an account? [Login](#Login)")

elif menu_selection == "Log Incident":
    if "logged_in" in st.session_state and st.session_state.logged_in:
        st.title("Log Incident")
        date = st.date_input("Date of Incident")
        time = st.time_input("Time of Incident")
        location = st.text_input("Location")
        incident_category = st.selectbox("Incident Category", sorted(INCIDENT_MAPPING.keys()))
        incident_subcategory = st.selectbox("Incident Subcategory", get_subcategories(incident_category))
        description = st.text_area("Description (optional)")
        police_district = st.selectbox("Police District", POLICE_DISTRICTS)
        if st.button("Submit"):
            log_incident(date, time, location, incident_category, incident_subcategory, description, police_district)
        st.markdown("<hr/>", unsafe_allow_html=True)
        if st.button("Log Out"):
            log_out()
    else:
        st.error("You need to log in to log an incident.")
        st.markdown("<hr/>", unsafe_allow_html=True)
        #st.write("Don't have an account? [Sign Up](#Sign-Up)")

elif menu_selection == "Crime Data Map":
    if "logged_in" in st.session_state and st.session_state.logged_in:
        st.title("Crime Data Map")
        st.write("Going to def")
        fetch_crime_data()
        st.markdown("<hr/>", unsafe_allow_html=True)

elif menu_selection == "Log Out":
    st.title("Log Out")
    if st.button("Log Out"):
        log_out()