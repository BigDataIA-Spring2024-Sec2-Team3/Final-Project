import streamlit as st
import pandas as pd
import leafmap.foliumap as leafmap
from .snowflake_operations import fetch_crime_data

def heat_map():
    if "logged_in" in st.session_state and st.session_state.logged_in:
        st.title('Heatmaps')
        grouped_df = fetch_crime_data()
        #st.write(grouped_df)
        m = leafmap.Map(center=[37.763, -122.47], zoom=12.2)
        m.add_heatmap(
            grouped_df, #type: ignore 
            latitude="latitude",
            longitude="longitude",
            value="size",
            name="Heat map",
            radius=20,
        )
        m.to_streamlit()

if __name__ == "__main__":
    heat_map()
