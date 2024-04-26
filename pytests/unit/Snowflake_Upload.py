import pytest
from unittest.mock import patch, MagicMock
import Airflow
from Airflow.plugins import upload_snowflake, create_engine


# Mock Snowflake connection parameters
user = 'test_user'
password = 'test_password'
account_identifier = 'test_account_identifier'

# Mock Snowflake SQL queries
create_stage = "CREATE STAGE ..."
create_table_query = "CREATE TABLE ..."
upload_to_stage = "UPLOAD TO STAGE ..."
copy_stage_to_table = "COPY INTO ..."

@pytest.fixture
def mock_create_engine():
    with patch('your_module.create_engine') as mock_create_engine:
        yield mock_create_engine

def test_upload(mock_create_engine):
    # Mock Snowflake connection
    mock_connection = MagicMock()
    mock_create_engine.return_value.connect.return_value = mock_connection

    # Call the upload function
    upload_snowflake.pulldata()

    # Assertions
    mock_create_engine.assert_called_once_with(
        f"snowflake://{user}:{password}@{account_identifier}/"
    )
    mock_connection.connect.assert_called_once()
    mock_connection.execute.assert_any_call("USE WAREHOUSE SFCrimes")
    mock_connection.execute.assert_any_call("USE DATABASE CRIMES")
    mock_connection.execute.assert_any_call("USE SCHEMA PROD")
    mock_connection.execute.assert_any_call(create_stage)
    mock_connection.execute.assert_any_call(create_table_query)
    mock_connection.execute.assert_any_call(upload_to_stage)
    mock_connection.execute.assert_any_call(copy_stage_to_table)
    mock_connection.close.assert_called_once()
