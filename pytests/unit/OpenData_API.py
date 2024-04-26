import pytest
from Airflow.plugins import (
    download_pdf,
    Law_PDF_Scrapping,
    Pinecone_Upsert,
    prapare_data,
    upload_snowflake
)
import pytest
import requests

# Define the mock API URL
MOCK_API_URL = "https://mockapi.com/data"

# Define sample data for testing
sample_data = [{"field1": "value1", "field2": "value2"}, {"field1": "value3", "field2": "value4"}]

@pytest.fixture
def mock_api_response(requests_mock):
    # Mock the API response
    requests_mock.get(MOCK_API_URL, json=sample_data)

def test_pulldata(mock_api_response):
    # Call the pulldata function
    result = prapare_data.pulldata()

    # Assert that the result matches the sample data
    assert result == sample_data


