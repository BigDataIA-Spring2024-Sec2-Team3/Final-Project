import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
#to ignore warnings
import warnings
warnings.filterwarnings('ignore')
import requests
from pydantic import HttpUrl
import time, csv, sys, os
import datetime

def pulldata():
    # Define the URL of the OpenData API endpoint
    api_url = "https://data.sfgov.org/resource/wg3w-h783.json"
    limit = 50000 # Number of records per request
    offset = 0    # Initial offset value

    # Initialize an empty list to store data
    all_data = []

    # Loop until all records are fetched
    while True:
        # Send a GET request to the API endpoint with the current offset
        new_api_url = f"{api_url}?$limit={limit}&$offset={offset}"
        #print(new_api_url)
        response = requests.get(new_api_url)
        
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Convert the response JSON data to a Python dictionary
            data_dict = response.json()
            
            # Check if data is returned
            if len(data_dict) == 0:
                # No more data available, exit the loop
                break
            
            # Append the fetched data to the list
            all_data.extend(data_dict)
            
            # Increment the offset for the next request
            offset += 50000
            
        else:
            print("Failed to retrieve data from the API endpoint. Status code:", response.status_code)
            break

    # Convert the list of dictionaries to a pandas DataFrame
    data = pd.DataFrame(all_data)

    # Perform further data processing or analysis as needed
    # Example:
    print("Number of records fetched:", len(data))

    data = data.drop([':@computed_region_26cr_cadq',':@computed_region_qgnn_b9vv', ':@computed_region_jwn9_ihcz'], axis = 1)
    data = data.drop([':@computed_region_h4ep_8xdi',':@computed_region_nqbw_i6c3', ':@computed_region_n4xg_c4py'], axis = 1)
    data = data.drop([':@computed_region_jg9y_a9du'], axis = 1)
    
    # timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    # # Construct file name with timestamp
    # csv_file = f"Incident_Reports_{timestamp}.csv"
    csv_file = "Incident_Reports.csv"
    data.to_csv(csv_file,index=False)
    
    return data




def main():
    data = pulldata()

if __name__ == "__main__":
    main()
    
