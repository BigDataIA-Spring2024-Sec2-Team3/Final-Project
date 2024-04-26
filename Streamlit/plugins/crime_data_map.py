import streamlit as st
from .snowflake_operations import fetch_crime_data

def crime_data_map():
    if "logged_in" in st.session_state and st.session_state.logged_in:
            st.title("Crime Data Map")
            grouped_df = fetch_crime_data()
            if grouped_df is not None:
                st.map(grouped_df.rename(columns={'latitude': 'lat', 'longitude': 'lon', 'size': 'size'}))
            else:
                st.error("No data available.")
            st.markdown("<hr/>", unsafe_allow_html=True)
    else:
            st.error("You need to log in to view the crime data map.")

if __name__ == "__main__":
    crime_data_map()
