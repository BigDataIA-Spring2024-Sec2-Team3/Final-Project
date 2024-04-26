import unittest
from unittest.mock import patch
from Airflow.plugins.prapare_data import pulldata

class TestAPI(unittest.TestCase):
    @patch('your_application.requests.get')
    def test_get_sf_crime_data(self, mock_get):
        mock_get.return_value.json.return_value = {"data": [...]}

        result = pulldata()
        self.assertEqual(result, {"data": [...]})
