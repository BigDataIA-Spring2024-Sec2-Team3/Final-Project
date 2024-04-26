import streamlit as st
import pandas as pd
import leafmap.foliumap as leafmap
from .snowflake_operations import fetch_heatmap_crime_data


def heat_map():
    if "logged_in" in st.session_state and st.session_state.logged_in:
        st.title('Heatmaps')
        option = st.selectbox('Select different types of metrics',('Days of Week','Time of Day','Holidays','Year', 'Category'))
        data, elements = fetch_heatmap_crime_data(option)
        selection = st.select_slider(f'For the metric: {option}',options=elements)
        filtered_df = data[data['Column0']==selection]
        m = leafmap.Map(center=[37.77, -122.44], zoom=13)
        m.add_heatmap(
            filtered_df, #type: ignore 
            latitude="latitude",
            longitude="longitude",
            value="size",
            name="Heat map",
            radius=20,
        )
        m.add_markers_from_xy(data, #type: ignore 
            latitude="latitude",
            longitude="longitude")
        m.to_streamlit()

if __name__ == "__main__":
    heat_map()
