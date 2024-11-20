# -*- coding: utf-8 -*-

info = """
###############################################################
TOKEN HOLDERS v.4
This script will get all holders of a native Cardano token
and save it to a local excel file (for further analysis)

The script utilizes the BLOCKFROST API
(get yours at https://blockfrost.io/)

You need to feed the token "encoded name" (Cexplorer.io)

@author: kostas_panagias (https://x.com/kostas_panagias)

Creation Date: 2024.09.10
Last Update: 2024.09.13
###############################################################

"""
import requests
import time
import pandas as pd
from decimal import Decimal, getcontext
import os
from dotenv import load_dotenv

from openpyxl import load_workbook
from openpyxl.styles import Alignment

print(info)

# Load environment variables from local ".env" file - This file contains BLOCKFROST API KEY
#.env exact contents: "BLOCKFROST_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" where xxx is your key
load_dotenv()

# Get the API key from environment variables
BLOCKFROST_API_KEY = os.getenv('BLOCKFROST_API_KEY')

# Set precision for Decimal operations
getcontext().prec = 28  # Adjust the precision if needed

# Blockfrost API base URL for Cardano mainnet
base_url = 'https://cardano-mainnet.blockfrost.io/api/v0'

# Function to get the token's decimal places from its metadata
def get_token_decimals(token_unit):
    headers = {
        'project_id': BLOCKFROST_API_KEY
    }
    
    # Blockfrost API endpoint to get token metadata
    metadata_url = f'{base_url}/assets/{token_unit}'
    response = requests.get(metadata_url, headers=headers)
    
    if response.status_code == 200:
        global metadata
        metadata = response.json()
        
        # Access the nested dictionary 'metadata' if it exists and is not None
        inner_metadata = metadata.get('metadata', {})
        
        if inner_metadata is not None:
            # Fetch the 'decimals' value from the nested dictionary
            decimals = inner_metadata.get('decimals', 0)  # Return 0 if 'decimals' is not found
            return int(decimals) if decimals is not None else 0
        else:
            # If 'metadata' is None, print a message and return 0
            print("No metadata found; defaulting decimals to 0.")
            return 0
    else:
        print(f"Error fetching token metadata: {response.status_code}")
        return 0


# Function to fetch token holders
def get_token_holders(token_unit, decimals, delay=1):
    headers = {
        'project_id': BLOCKFROST_API_KEY
    }

    page = 1  # Start from the first page
    all_holders = []

    while True:
        # Blockfrost API endpoint to get token holders with pagination
        holders_url = f'{base_url}/assets/{token_unit}/addresses?page={page}'
        response = requests.get(holders_url, headers=headers)

        if response.status_code == 200:
            holders = response.json()
            
            if not holders:
                # If no more data, break the loop
                break

            # Accumulate all holders
            all_holders.extend(holders)
            print(f"Fetched page {page} with {len(holders)} holders.")

            # Increment the page number to fetch the next page
            page += 1

            # Respect rate limit with a delay
            time.sleep(delay)
        else:
            print(f"Error fetching token holders on page {page}: {response.status_code}")
            break

    # Create a pandas DataFrame from the holders data
    df = pd.DataFrame(all_holders)

    # Ensure the columns are named correctly
    df = df.rename(columns={'address': 'Address', 'quantity': 'Quantity'})

    # Adjust Quantity using the number of decimals
    factor = Decimal(10) ** Decimal(decimals)  # Use Decimal for the factor to maintain precision
    df['Adjusted Quantity'] = df['Quantity'].apply(lambda x: Decimal(str(x)) / factor)

    # Sort the DataFrame by Adjusted Quantity in descending order
    df = df.sort_values(by='Adjusted Quantity', ascending=False)


    # Convert the 'Adjusted Quantity' column to floats
    df['Adjusted Quantity'] = df['Adjusted Quantity'].astype(float)
    # Now apply rounding to x decimal places
    df['Adjusted Quantity'] = df['Adjusted Quantity'].round(decimals)

    # Keep only the 'Adjusted Quantity' column
    df.drop(columns=['Quantity'], inplace=True)
    df.rename(columns={'Adjusted Quantity': 'Quantity'}, inplace=True)

    return df



if __name__ == "__main__":
    # Replace with your token unit (unique identifier of the token) & ticker
    #token_list = ['f3fc8638cb9b0016c979cb5543d74264e798b59dce5a66e2c49b008847494741534e454b','Gigasnek']
    #token_list = ['5d16cc1a177b5d9ba9cfa9793b07e60f1fb70fea1f8aef064415d114494147','IAG']
    #token_list = ['f43a62fdc3965df486de8a0d32fe800963589c41b38946602a0dc53541474958','agix']
    #token_list = ['141eea77e407aa35eec384dd6d863ca44aa338273222403c8f5549d9446f6e67','dong']
    #token_list = ['815418a1b078a259e678ecccc9d7eac7648d10b88f6f75ce2db8a25a4672616374696f6e2045737461746520546f6b656e','FET']
    #token_list = ['676fe95d29c1fa198f86c862def5bf7a487c8abf04c3b0b53bdd1bf3','GYROS']
    token_list = ['27526d00b52e27a0cdbf3558dc96a5e802e68be2ae435b88ae5ffe5453616c74795468654d6173636f74','SALTY']
    

    token_unit = token_list[0]
    token = token_list[1]
    
    # Fetch the token's metadata to get the number of decimals
    decimals = get_token_decimals(token_unit)

    # Fetch the token holders and create a DataFrame
    df = get_token_holders(token_unit, decimals)
    
    df.to_excel(f'{token}_holders.xlsx', index=False)
    print(f"Data has been saved to {token}_holders.xlsx'.")

    print('starting formats')
    # Load the existing Excel file
    workbook = load_workbook(f'{token}_holders.xlsx')
    worksheet = workbook.active  # Assuming you want to modify the first sheet
    
    # Set the width of the first column (column A) to 120
    worksheet.column_dimensions['A'].width = 120
    worksheet.column_dimensions['B'].width = 23
    
    # Apply the number format to the second column (column B)
    for cell in worksheet['B']:
        cell.number_format = f"#,##0.{'0' * decimals}"
        # Optional: Align the cell contents to the right
        cell.alignment = Alignment(horizontal='right')
    
    # Save the changes
    workbook.save(f'{token}_holders.xlsx')
    print('finished formats')
