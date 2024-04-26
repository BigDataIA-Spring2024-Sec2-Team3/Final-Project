import streamlit as st
from plugins.registration_login import show_registration_login, log_out
# import plugins.ai_law_help as ai_law_help
from plugins.heat_map import heat_map
from plugins.dashboard import fetch_data, dashboard
import os

# Set page configuration
st.set_page_config(
    page_title="California Crime",
    page_icon="🚓",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "logged_in" not in st.session_state:
     st.session_state.logged_in = False
     

if not st.session_state.logged_in:
    show_registration_login()
else:
    # Define the layout of the page
    #st.title("")
    st.sidebar.title("Navigation")

    # Menu selection
    menu_selection = st.sidebar.radio(
    "Go to:",
    ("Crime Dashboard", "Heat Map", "AI Law Help"))

    # Add logout button at the bottom of the sidebar
    if st.sidebar.button("Log Out", key="logout_button"):
        log_out()
    
    if menu_selection == "Crime Dashboard":
        if "logged_in" in st.session_state and st.session_state.logged_in:
            dashboard()

        # Menu options
    if menu_selection == "Heat Map":
        heat_map()
        
    # elif menu_selection == "AI Law Help":
    #     ai_law_help

# Add custom CSS for dark theme and serif font
st.markdown(
    """
    <style>
    /* Dark theme */
    body {
        color: #FFFFFF; /* Text color */
        background-color: #121212; /* Background color */
    }
    .stApp {
        background-color: #000000; /* Black background */
    }
    .sidebar-content {
        background-color: #121212 !important; /* Sidebar background color */
    }
    .sidebar-content .block-container {
        color: #FFFFFF !important; /* Color of sidebar elements */
    }
    .stMarkdown, .stBlockquote {
        color: #FFFFFF !important; /* Color of main content */
    }

    /* Serif font */
    body {
        font-family: serif; /* Set font to serif */
    }

    /* Additional styling */
    .stButton>button {
        border-radius: 15px !important;
        padding: 10px 20px !important;
        font-size: 16px !important;
        color: #FFFFFF !important; /* White text */
        background-color: #FF0000 !important; /* Red button */
        border-color: #FF0000 !important;
        transition: background-color 0.4s ease !important;
        font-weight: bold; /* Added bold font weight */
    }
    .stButton>button:hover {
        background-color: #CC0000 !important; /* Darker red on hover */
    }
    .stSelectbox>div>div>div>select {
        border-radius: 15px !important;
        padding: 12px 20px !important;
        font-size: 16px !important;
        color: #FFFFFF !important; /* White text */
        background-color: #FF0000 !important; /* Red dropdown */
        border-color: #FF0000 !important;
        font-weight: bold; /* Added bold font weight */
    }
    .stTextInput>div>div>input, .stTextArea>div>textarea, .stDateInput>div>input, .stTimeInput>div>input {
        border-radius: 15px !important;
        padding: 12px 20px !important;
        font-size: 16px !important;
        color: #FFFFFF !important; /* White text */
        background-color: #202020 !important; /* Light gray background */
        border-color: #FFFFFF !important; /* White border */
        font-weight: bold; /* Added bold font weight */
    }
    </style>
    """,
    unsafe_allow_html=True
)
