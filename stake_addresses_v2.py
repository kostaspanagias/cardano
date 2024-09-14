# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 08:18:38 2024

@author: kpanagias
"""

info = """
###############################################################
STAKE KEY ADDRESSES
This script will read a csv file with a list of stake keys and
get all the addresses of each stake key exported into an Excel 
file for further analysis.

The script utilizes the BLOCKFROST API
(get yours at https://blockfrost.io/)


csv file should be in the format:
----------------------------------------------------------
stake_address
stakexxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
stakezzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz
----------------------------------------------------------


@author: kostas_panagias (https://x.com/kostas_panagias)

Creation Date: 2024.09.11
Last Update: 2024.09.14
###############################################################

"""


import pandas as pd
import requests
import os
from dotenv import load_dotenv

print(info)

# Load environment variables from local ".env" file - This file contains BLOCKFROST API KEY
#.env exact contents: "BLOCKFROST_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" where xxx is your key
load_dotenv()

# Get the API key from environment variables
BLOCKFROST_API_KEY = os.getenv('BLOCKFROST_API_KEY')

BASE_URL = 'https://cardano-mainnet.blockfrost.io/api/v0'

# Function to fetch addresses and ADA amounts for a given stake address
# Function to fetch addresses and ADA amounts for a given stake address
def fetch_addresses_for_stake(stake_address):
    headers = {
        'project_id': BLOCKFROST_API_KEY
    }
    
    # Initialize an empty list to store all addresses
    all_addresses_list = []
    page = 1  # Start from the first page

    while True:
        # Fetch addresses associated with the stake address with pagination
        url = f"{BASE_URL}/accounts/{stake_address}/addresses?page={page}"

        # Debug: Print the full URL
        print(f"Request URL: {url}")
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            addresses_data = response.json()

            # If no more data is returned, break the loop
            if not addresses_data:
                break

            # Process the fetched addresses
            for address_info in addresses_data:
                address = address_info['address']
                ada_amount = fetch_ada_amount(address)
                all_addresses_list.append((address, ada_amount))
            
            # Move to the next page
            page += 1
        else:
            print(f"Failed to fetch addresses for {stake_address}: {response.status_code}")
            break

    return all_addresses_list

# Function to fetch ADA amount for a given address
def fetch_ada_amount(address):
    headers = {
        'project_id': BLOCKFROST_API_KEY
    }
    
    # Fetch address details to get ADA amount
    url = f"{BASE_URL}/addresses/{address}"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        address_data = response.json()
        return int(address_data['amount'][0]['quantity']) / 1_000_000  # Convert Lovelace to ADA
    else:
        print(f"Failed to fetch ADA amount for {address}: {response.status_code}")
        return 0

# Main function to read CSV and write results to Excel
def main():
    # Read the CSV file with stake addresses
    df = pd.read_csv('stake.csv')
    
    output_data = []
    
    # Iterate over each stake address
    for stake_address in df['stake_address']:
        addresses_list = fetch_addresses_for_stake(stake_address)
        for address, ada_amount in addresses_list:
            output_data.append({
                'stake_pool_address': stake_address,
                'addresses': address,
                'ada_amount': ada_amount
            })

    # Convert output data to a DataFrame
    output_df = pd.DataFrame(output_data)
    
    # Save to Excel file
    output_df.to_excel('cardano_addresses_output.xlsx', index=False)

if __name__ == '__main__':
    main()
