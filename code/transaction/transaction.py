import requests
import os
from dotenv import load_dotenv
from datetime import datetime
import pandas as pd

# Load environment variables from local ".env" file
load_dotenv()

# Get the API key from environment variables
BLOCKFROST_API_KEY = os.getenv('BLOCKFROST_API_KEY')

BASE_URL = 'https://cardano-mainnet.blockfrost.io/api/v0'

def fetch_transaction_details(tx_id):
    headers = {
        'project_id': BLOCKFROST_API_KEY
    }
    
    # Endpoint to get transaction details
    tx_url = f"{BASE_URL}/txs/{tx_id}"
    tx_response = requests.get(tx_url, headers=headers)
    
    if tx_response.status_code == 200:
        tx_data = tx_response.json()
    else:
        print(f"Failed to fetch transaction details: {tx_response.status_code}")
        return None

    # Get the date of the transaction
    block_url = f"{BASE_URL}/blocks/{tx_data['block']}"
    block_response = requests.get(block_url, headers=headers)
    
    if block_response.status_code == 200:
        block_data = block_response.json()
        # Format the date to 'yyyy.mm.dd - HH.MM.SS'
        tx_date = datetime.fromtimestamp(block_data['time']).strftime('%Y.%m.%d - %H.%M.%S')
    else:
        print(f"Failed to fetch block details: {block_response.status_code}")
        return None

    # Endpoint to get transaction UTXOs (inputs and outputs)
    utxo_url = f"{BASE_URL}/txs/{tx_id}/utxos"
    utxo_response = requests.get(utxo_url, headers=headers)
    
    if utxo_response.status_code == 200:
        utxo_data = utxo_response.json()
    else:
        print(f"Failed to fetch transaction UTXOs: {utxo_response.status_code}")
        return None

    # Fetch stake keys for wallets
    def fetch_stake_key(address):
        url = f"{BASE_URL}/addresses/{address}"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            address_data = response.json()
            return address_data.get('stake_address', 'N/A')
        else:
            return 'N/A'

    # Prepare inputs and outputs details
    inputs_details = []
    outputs_details = []
    tokens_moved = []

    # Process inputs (senders)
    for input_data in utxo_data['inputs']:
        sender_wallet = input_data['address']
        sender_stake_key = fetch_stake_key(sender_wallet)
        ada_amount = int(input_data['amount'][0]['quantity']) / 1_000_000  # Convert Lovelace to ADA
        
        inputs_details.append({
            'Address': sender_wallet,
            'Stake Key': sender_stake_key,
            'ADA Amount': ada_amount
        })

    # Process outputs (receivers)
    for output in utxo_data['outputs']:
        receiver_wallet = output['address']
        receiver_stake_key = fetch_stake_key(receiver_wallet)
        receiver_ada_amount = int(output['amount'][0]['quantity']) / 1_000_000

        outputs_details.append({
            'Address': receiver_wallet,
            'Stake Key': receiver_stake_key,
            'ADA Amount': receiver_ada_amount
        })

        # Process tokens for each output
        for amount in output['amount'][1:]:  # Skip the first ADA amount
            token_name_url = f"{BASE_URL}/assets/{amount['unit']}"
            token_response = requests.get(token_name_url, headers=headers)
            token_name = token_response.json().get('fingerprint', 'N/A') if token_response.status_code == 200 else 'N/A'
            
            tokens_moved.append({
                'Input Address': sender_wallet,
                'Input Stake Key': sender_stake_key,
                'Output Address': receiver_wallet,
                'Output Stake Key': receiver_stake_key,
                'Token': amount['unit'],
                'Token Name': token_name,
                'Quantity': int(amount['quantity'])
            })

    # Get the transaction fee
    transaction_fee = int(tx_data['fees']) / 1_000_000  # Convert Lovelace to ADA

    transaction_info = {
        'tx_id': tx_id,
        'date': tx_date,
        'inputs_details': inputs_details,
        'outputs_details': outputs_details,
        'tokens_moved': tokens_moved,
        'transaction_fee': transaction_fee
    }

    return transaction_info

def save_transaction_to_excel(transaction_info):
    if not transaction_info:
        print("No transaction info to save.")
        return

    # Create DataFrames for ADA and token transactions
    ada_df = pd.DataFrame(transaction_info['inputs_details'] + transaction_info['outputs_details'])
    ada_df['Transaction Fee'] = transaction_info['transaction_fee']
    ada_df['Date'] = transaction_info['date']
    ada_df['Type'] = ['Input'] * len(transaction_info['inputs_details']) + ['Output'] * len(transaction_info['outputs_details'])

    token_df = pd.DataFrame(transaction_info['tokens_moved'])

    # Create an Excel writer object and save the DataFrames to two sheets
    filename = f"{transaction_info['tx_id']}.xlsx"
    with pd.ExcelWriter(filename) as writer:
        ada_df.to_excel(writer, sheet_name='ADA Transactions', index=False)
        token_df.to_excel(writer, sheet_name='Token Transactions', index=False)

    print(f"Transaction details saved to {filename}")

if __name__ == "__main__":
    # Example usage
    tx_id = input("Enter the transaction ID: ")
    result = fetch_transaction_details(tx_id)
    
    if result:
        save_transaction_to_excel(result)
