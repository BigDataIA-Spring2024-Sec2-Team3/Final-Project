from plotly.graph_objs._figure import Figure
import streamlit as st
import pandas as pd
import snowflake.connector
import altair as alt
from dotenv import load_dotenv
import os 
import plotly.express as px

load_dotenv(override=True)

snowflake_user = os.getenv("SNOWFLAKE_USER")
snowflake_password = os.getenv("SNOWFLAKE_PASSWORD")
snowflake_account = os.getenv("SNOWFLAKE_ACCOUNT")
snowflake_database = os.getenv("SNOWFLAKE_DATABASE")
snowflake_schema = os.getenv("SNOWFLAKE_SCHEMA")

@st.cache_data
def fetch_data(years=None):
    # Replace the following parameters with your Snowflake credentials
    conn = snowflake.connector.connect(
        user=snowflake_user,
        password=snowflake_password,
        account=snowflake_account,
        database=snowflake_database,
        schema=snowflake_schema
    )
    if years is None:
        # No years selected, fetch data for all years
        sql_query = """
        SELECT
            INCIDENT_DATETIME,
            INCIDENT_DATE,
            INCIDENT_TIME,
            INCIDENT_YEAR,
            INCIDENT_DAY_OF_WEEK,
            REPORT_DATETIME,
            INCIDENT_ID,
            INCIDENT_NUMBER,
            INCIDENT_CATEGORY,
            INCIDENT_SUBCATEGORY,
            INCIDENT_DESCRIPTION,
            RESOLUTION,
            POLICE_DISTRICT,
            ANALYSIS_NEIGHBORHOOD
        FROM INCIDENT_REPORTS
        """
    else:
        # Convert years list to a comma-separated string
        years_str = ', '.join([str(year) for year in years])

        # SQL query to fetch incident data for selected years
        sql_query = f"""
        SELECT
            INCIDENT_DATETIME,
            INCIDENT_DATE,
            INCIDENT_TIME,
            INCIDENT_YEAR,
            INCIDENT_DAY_OF_WEEK,
            REPORT_DATETIME,
            INCIDENT_ID,
            INCIDENT_NUMBER,
            INCIDENT_CATEGORY,
            INCIDENT_SUBCATEGORY,
            INCIDENT_DESCRIPTION,
            RESOLUTION,
            POLICE_DISTRICT,
            ANALYSIS_NEIGHBORHOOD
        FROM INCIDENT_REPORTS
        WHERE INCIDENT_YEAR IN ({years_str})
        """

    # Execute query and fetch data into a DataFrame
    df = pd.read_sql(sql_query, conn)
    return df

def dashboard():

    df = fetch_data()
    # Filter out null values before applying sorted()
    filtered_neighborhoods = df['ANALYSIS_NEIGHBORHOOD'].dropna()

    st.title('Crime Dashboard')
    # Sidebar filters
    st.sidebar.header('Filters')
    years = range(2018, 2024)
    selected_years = st.sidebar.multiselect('Select Year', years, default=years)
    selected_day_of_week = st.sidebar.multiselect('Select Day of Week', sorted(df['INCIDENT_DAY_OF_WEEK'].unique()), default=sorted(df['INCIDENT_DAY_OF_WEEK'].unique()))
    #selected_location = st.sidebar.multiselect('Select Location', sorted(filtered_neighborhoods.unique()), default=sorted(filtered_neighborhoods.unique()))
    selected_report_status = st.sidebar.multiselect('Select Report Status', df['RESOLUTION'].unique(), default=df['RESOLUTION'].unique())

    # Add police district filter
    selected_police_district = st.sidebar.multiselect('Select Police District', sorted(df['POLICE_DISTRICT'].unique()), default=sorted(df['POLICE_DISTRICT'].unique()))

    # Add month filter
    # Extract month from INCIDENT_DATETIME and convert it to string
    df['Year-Month'] = pd.to_datetime(df['INCIDENT_DATETIME']).dt.to_period('M').astype(str)
    #selected_month = st.sidebar.multiselect('Select Month', sorted(df['Year-Month'].unique()), default=sorted(df['Year-Month'].unique()))

    
    # Apply filters
    filtered_df = df[(df['INCIDENT_YEAR'].isin(selected_years)) &
                     (df['INCIDENT_DAY_OF_WEEK'].isin(selected_day_of_week)) &
                    # (df['ANALYSIS_NEIGHBORHOOD'].isin(selected_location)) &
                     (df['RESOLUTION'].isin(selected_report_status)) &
                     (df['POLICE_DISTRICT'].isin(selected_police_district)) 
                    # (df['Year-Month'].isin(selected_month))
                    ]

    # Data visualization
    st.header('Data Visualization')

    # Row 1: Incidents by Day of Week and Incidents by Year
    col1, col2 = st.columns(2)
    with col1:
        st.subheader('Incidents by Day of Week')
        day_of_week_counts = df['INCIDENT_DAY_OF_WEEK'].value_counts()
        st.bar_chart(day_of_week_counts)

    with col2:
        st.subheader('Incidents by Year')
        year_counts = df['INCIDENT_YEAR'].value_counts()
        st.bar_chart(year_counts)

    # Row 2: Top 15 Incident Categories and Interactive Bar Chart
    col3, col4 = st.columns(2)
    with col3:
        st.subheader('Top 15 Incident Categories')        
        # Get the top 15 incident categories in descending order of count
        top_categories = df['INCIDENT_CATEGORY'].value_counts().sort_values(ascending=False).head(15)
        
        fig: Figure = px.pie(
            top_categories,
            values='count',
            names=top_categories.index,  # Use category names as labels
            title="Top 15 Incident Categories",
        )
        
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        st.subheader('Interactive Bar Chart')
        chart_data = df.groupby('INCIDENT_SUBCATEGORY').size().nlargest(15).reset_index(name='count') #type:ignore
        chart = alt.Chart(chart_data).mark_bar().encode(
            x='count',
            y=alt.Y('INCIDENT_SUBCATEGORY', sort='-x'),
            tooltip=['INCIDENT_SUBCATEGORY', 'count']
        ).properties(width=600, height=300)
        st.altair_chart(chart)

    # Row 3: Yearly Crime Trend and Resolution of Cases
    col5, col6 = st.columns(2)
    with col5:
        st.subheader('Yearly Crime Trend')
        yearly_trend = df['INCIDENT_YEAR'].value_counts().sort_index()
        st.line_chart(yearly_trend)

    with col6:
        st.header('Resolution of Cases')
        # Calculate counts for each resolution category
        resolution_counts = df['RESOLUTION'].value_counts()

        # Create a pie chart
        fig = px.pie(resolution_counts, values=resolution_counts.values, names=resolution_counts.index, 
                    title='Distribution of Incident Resolutions')
        st.plotly_chart(fig, use_container_width=True)

    # Row 4: Top Crime Locations and Incidents by Police District
    col7, col8 = st.columns(2)
    with col7:
        st.subheader('Top Crime Locations')
        top_locations = df['ANALYSIS_NEIGHBORHOOD'].value_counts().head(15)
        st.bar_chart(top_locations)

    with col8:
        st.subheader('Incidents by Police District')
        # Group by police district and count incidents
        district_counts = df['POLICE_DISTRICT'].value_counts().reset_index(name='Incident Count')  #type: ignore
        # Plot bar chart for police districts
        district_counts = district_counts.reset_index()  # Reset index before plotting
        fig = px.bar(district_counts, x='POLICE_DISTRICT', y='Incident Count', title='Incidents by Police District',
                        labels={'district_counts.index': 'Police District', 'Incident Count': 'Incident Count'})
        fig.update_traces(marker=dict(color='orange'))
        st.plotly_chart(fig, use_container_width=True)

    # Row 5: Monthly Crime Analysis
    st.header('Monthly Crime Analysis')
    monthly_counts = df.groupby('Year-Month').size().reset_index(name='Incident Count') #type: ignore
    fig = px.line(monthly_counts, x='Year-Month', y='Incident Count', title='Monthly Crime Incidents',
                  labels={'Year-Month': 'Month-Year', 'Incident Count': 'Incident Count'})
    fig.update_xaxes(ticklabelmode='period')
    st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    dashboard()
