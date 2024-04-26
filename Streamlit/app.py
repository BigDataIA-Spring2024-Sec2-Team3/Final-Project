# import streamlit as st
# import snowflake.connector
# from dotenv import load_dotenv
# import os
# import hashlib
# import re
# import requests
# import pandas as pd
# import leafmap.foliumap as leafmap
# from openai import OpenAI

# # Load environment variables
# load_dotenv(override=True)

# # Snowflake credentials
# snowflake_user = os.getenv("SNOWFLAKE_USER")
# snowflake_password = os.getenv("SNOWFLAKE_PASSWORD")
# snowflake_account = os.getenv("SNOWFLAKE_ACCOUNT")
# snowflake_database = os.getenv("SNOWFLAKE_DATABASE")
# snowflake_schema = os.getenv("SNOWFLAKE_SCHEMA")
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# # Initialize session state
# if "logged_in" not in st.session_state:
#     st.session_state.logged_in = False

# # Streamlit UI
# st.set_page_config(
#     page_title="Crime Incident Logger",
#     page_icon="🚓",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # Styling
# st.markdown(
#     """
#     <style>
#     .stApp {
#         background-color: #FFFFFF; /* White background */
#     }
#     .stButton>button {
#         border-radius: 15px !important;
#         padding: 8px 16px !important;
#         font-size: 16px !important;
#         color: #FFFFFF !important; /* White text */
#         background-color: #FF5555 !important; /* Red button */
#         border-color: #FF5555 !important;
#         transition: background-color 0.4s ease !important;
#     }
#     .stButton>button:hover {
#         background-color: #FF3333 !important; /* Darker red on hover */
#     }
#     .stTextInput>div>div>input {
#         border-radius: 15px !important;
#         padding: 10px 15px !important;
#         font-size: 16px !important;
#     }
#     .stSelectbox>div>div>div>select {
#         border-radius: 15px !important;
#         padding: 10px 15px !important;
#         font-size: 16px !important;
#     }
#     .stTextArea>div>textarea {
#         border-radius: 15px !important;
#         padding: 10px 15px !important;
#         font-size: 16px !important;
#     }
#     .stDateInput>div>input {
#         border-radius: 15px !important;
#         padding: 10px 15px !important;
#         font-size: 16px !important;
#     }
#     .stTimeInput>div>input {
#         border-radius: 15px !important;
#         padding: 10px 15px !important;
#         font-size: 16px !important;
#     }
#     </style>
#     """,
#     unsafe_allow_html=True
# )

# # Log out function
# def log_out():
#     st.session_state.logged_in = False
#     st.session_state.user_id = None
#     st.success("Logged out successfully!")
#     st.experimental_rerun()

# # Fetching crime data
# def fetch_crime_data():
#     try:
#         with st.spinner("Loading"):
#             response = requests.get("http://fastapi2:8075/snowflake-data")
#             data = response.json()['data']
            
#             if data:
#                 df = pd.DataFrame(data, columns=['Column0','latitude', 'longitude', 'year'])
#                 df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
#                 df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')

#                 grouped_df = df.groupby(by=['latitude', 'longitude']).size().reset_index(name='count') # type: ignore

#                 #st.write("Aggregated Locations with Count:")
#                 #st.write(grouped_df.head())

#                 grouped_df['size'] = grouped_df['count'].apply(lambda x: x * 10)  # Scale factor example

#                 return grouped_df
#             else:
#                 st.write("No data available.")
#     except Exception as e:
#         st.error(f"An error occurred while fetching crime data: {e}")


# # Function to connect to Snowflake
# def connect_to_snowflake():
#     conn = None
#     cursor = None
#     try:
#         conn = snowflake.connector.connect(
#             user=snowflake_user,
#             password=snowflake_password,
#             account=snowflake_account,
#             database=snowflake_database,
#             schema=snowflake_schema
#         )
#         cursor = conn.cursor()
#     except Exception as e:
#         st.error(f"An error occurred while connecting to Snowflake: {e}")
#     return conn, cursor

# def show_registration_login():
#     if not st.session_state.logged_in:
#         # Define the layout of the page
#         st.title("User Registration and Login")
#         col1, col2 = st.columns(2)

#         # User registration
#         with col1:
#             # Registration form
#             st.header("User Registration")
#             new_username = st.text_input("New Username")
#             new_password = st.text_input("New Password", type="password")
#             full_name = st.text_input("Full Name")
#             email = st.text_input("Email")
#             role = st.selectbox("Role", ["User", "Admin"])

#             def register_new_user(username, password, full_name, email, role):
#                 conn, cursor = connect_to_snowflake()
#                 try:
#                     if conn is None or cursor is None:
#                         return False, "Failed to connect to the database."
                    
#                     # Validate email format
#                     if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
#                         return False, "Invalid email address"

#                     # Validate password criteria
#                     if len(password) < 8:
#                         return False, "Password must be at least 8 characters long"

#                     if not re.match(r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]+$", password):
#                         return False, "Password must contain at least one letter, one number, and one special character"

#                     hashed_password = hashlib.sha256(password.encode()).hexdigest()
#                     cursor.execute(f"INSERT INTO users_project (username, password, full_name, email, role) VALUES ('{username}', '{hashed_password}', '{full_name}', '{email}', '{role}')")
#                     conn.commit()
#                     return True, "Sign-up successful! Please proceed to login."
                    
#                 except Exception as e:
#                     return False, f"An error occurred: {e}"
#                 finally:
#                     if cursor:
#                         cursor.close()
#                     if conn:
#                         conn.close()
  

#             if st.button("Sign Up"):
#                 if not new_username or not new_password or not full_name or not email:
#                     st.error("Please fill in all fields.")
#                 else:
#                     success, message = register_new_user(new_username, new_password, full_name, email, role)
#                     if success:
#                         st.success(message)
#                         st.experimental_rerun()
#                     else:
#                         st.error(message)
#             st.markdown("<hr/>", unsafe_allow_html=True)

#         # User login
#         with col2:
#             # Login form
#             st.header("Login")
#             username = st.text_input("Username", key="login_username_input")
#             password = st.text_input("Password", type="password", key="login_password_input")
            
#             def validate_user_credentials(username, password):
#                 conn, cursor = connect_to_snowflake()
#                 try:
#                     if conn and cursor:
#                         cursor.execute(f"SELECT user_id, password, role FROM users_project WHERE username = '{username}'")
#                         result = cursor.fetchone()
#                         if result:
#                             user_id, stored_password, user_role = result
#                             hashed_password = hashlib.sha256(password.encode()).hexdigest()
#                             if hashed_password == stored_password:
#                                 return True, user_id, user_role
#                         return False, None, None
#                 except Exception as e:
#                     st.error(f"An error occurred: {e}")
#                 finally:
#                     if cursor:
#                         cursor.close()
#                     if conn:
#                         conn.close()
#                 return False, None, None

#             if st.button("Login", key="login_button"):
#                 if not username or not password:
#                     st.error("Please enter username and password.")
#                 else:
#                     success, user_id, user_role = validate_user_credentials(username, password)
#                     if success:
#                         st.success("Login successful!")
#                         st.success(f"Welcome, {username} ({user_role})!")
#                         # Update session state
#                         st.session_state.logged_in = True
#                         st.session_state.user_id = user_id
#                         st.session_state.user_role = user_role
#                     else:
#                         st.error("Incorrect username or password.")
#                     st.experimental_rerun()
#             st.markdown("<hr/>", unsafe_allow_html=True)

# if not st.session_state.logged_in:
#     show_registration_login()
# else:
#     # Define the layout of the page
#     st.title("Crime Incident Logger")
#     st.sidebar.title("Navigation")

#     # Menu selection
#     menu_selection = st.sidebar.radio(
#     "Go to:",
#     ("Crime Data Map", "Heat Map", "AI Law Help"))

#         # Menu options
#     if menu_selection == "Crime Data Map":
#         if "logged_in" in st.session_state and st.session_state.logged_in:
#             st.title("Crime Data Map")
#             grouped_df = fetch_crime_data()
#             if grouped_df is not None:
#                 st.map(grouped_df.rename(columns={'latitude': 'lat', 'longitude': 'lon', 'size': 'size'}))
#             else:
#                 st.error("No data available.")
#             st.markdown("<hr/>", unsafe_allow_html=True)
#         else:
#             st.error("You need to log in to view the crime data map.")

#     elif menu_selection == "Heat Map":
#         if "logged_in" in st.session_state and st.session_state.logged_in:
#             st.title('Heatmaps')
#             grouped_df = fetch_crime_data()
#             st.write(grouped_df)
#             m = leafmap.Map(center=[37.763, -122.47], zoom=12.2)
#             m.add_heatmap(
#                 grouped_df, # type: ignore
#                 latitude="latitude",
#                 longitude="longitude",
#                 value="size",
#                 name="Heat map",
#                 radius=20,
#             )
#             m.to_streamlit()
        

#     elif menu_selection == "AI Law Help":
#         if "logged_in" in st.session_state and st.session_state.logged_in:
#             st.title("AI Law Help")
#             client = OpenAI(api_key=OPENAI_API_KEY)

#             if "openai_model" not in st.session_state:
#                 st.session_state["openai_model"] = "gpt-3.5-turbo"

#             if "messages" not in st.session_state:
#                 st.session_state.messages = []

#             for message in st.session_state.messages:
#                 with st.chat_message(message["role"]):
#                     st.markdown(message["content"])

#             if prompt := st.chat_input("What is up?"):
#                 st.session_state.messages.append({"role": "user", "content": prompt})
#                 with st.chat_message("user"):
#                     st.markdown(prompt)

#                 with st.chat_message("assistant"):
#                     stream = client.chat.completions.create(
#                         model=st.session_state["openai_model"],
#                         messages=[
#                             {"role": m["role"], "content": m["content"]}
#                             for m in st.session_state.messages
#                         ],
#                         stream=True,
#                     )
#                     response = st.write_stream(stream)
#                 st.session_state.messages.append({"role": "assistant", "content": response})
            
#     # Add logout button at the bottom of the sidebar
#     if st.sidebar.button("Log Out", key="logout_button"):
#         log_out()

import streamlit as st
from plugins.registration_login import show_registration_login
from plugins.ai_law_help import ai_law_help
from plugins.heat_map import heat_map
from plugins.crime_data_map import crime_data_map
import os

# Set page configuration
st.set_page_config(
    page_title="California Crime",
    page_icon="🚓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS styling to Streamlit components
st.markdown(
    """
    <style>
    .stApp {
        background-color: #FFFFFF; /* White background */
    }
    .stButton>button {
        border-radius: 15px !important;
        padding: 8px 16px !important;
        font-size: 16px !important;
        color: #FFFFFF !important; /* White text */
        background-color: #FF5555 !important; /* Red button */
        border-color: #FF5555 !important;
        transition: background-color 0.4s ease !important;
    }
    .stButton>button:hover {
        background-color: #FF3333 !important; /* Darker red on hover */
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

if "logged_in" not in st.session_state:
     st.session_state.logged_in = False
     

if not st.session_state.logged_in:
    show_registration_login()
else:
    # Define the layout of the page
    st.title("Crime Incident Logger")
    st.sidebar.title("Navigation")

    # Menu selection
    menu_selection = st.sidebar.radio(
    "Go to:",
    ("Crime Data Map", "Heat Map", "AI Law Help"))

        # Menu options
    if menu_selection == "Crime Data Map":
        crime_data_map()

    elif menu_selection == "Heat Map":
        heat_map()
        
    elif menu_selection == "AI Law Help":
        ai_law_help()

    # Add logout button at the bottom of the sidebar
    if st.sidebar.button("Log Out", key="logout_button"):
        log_out()

#         [theme]
# primaryColor="#F63366"
# backgroundColor="#FFFFFF"
# secondaryBackgroundColor="#F0F2F6"
# textColor="#262730"
# font="sans serif"