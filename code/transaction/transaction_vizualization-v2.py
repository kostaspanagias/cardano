# -*- coding: utf-8 -*-

import os
import requests
import dash
import dash_cytoscape as cyto
from dash import html
from dotenv import load_dotenv
from datetime import datetime

info = """

This script visualizes the flow of assets in a Cardano transaction using Dash Cytoscape.
It fetches transaction data (inputs, outputs, ADA amounts, and metadata) from the Blockfrost API
and displays an interactive graph where each node represents a wallet or transaction.

Usage:
1. Install required libraries: `pip install dash dash-cytoscape requests python-dotenv`.
2. Add your Blockfrost API key in a `.env` file (BLOCKFROST_API_KEY=<your_api_key>).
3. Enter a valid Cardano transaction ID in the `tx_id` variable.
4. Run the script
5. Open the browser at `http://127.0.0.1:8050/` to interact with the graph.

@author: kostas_panagias (https://x.com/kostas_panagias)

Creation Date: 2024.09.19

"""

print(info)

# Load environment variables for the Blockfrost API key
load_dotenv()
BLOCKFROST_API_KEY = os.getenv('BLOCKFROST_API_KEY')
BASE_URL = 'https://cardano-mainnet.blockfrost.io/api/v0'

if not BLOCKFROST_API_KEY:
    raise ValueError("BLOCKFROST_API_KEY not found in environment variables.")

# Fetch transaction data (UTXOs and metadata)
def fetch_transaction_data(tx_id):
    headers = {'project_id': BLOCKFROST_API_KEY}
    
    # Fetch UTXOs (inputs and outputs)
    utxos_url = f"{BASE_URL}/txs/{tx_id}/utxos"
    utxos_response = requests.get(utxos_url, headers=headers)
    
    # Fetch transaction metadata
    tx_url = f"{BASE_URL}/txs/{tx_id}"
    tx_response = requests.get(tx_url, headers=headers)
    
    if utxos_response.status_code == 200 and tx_response.status_code == 200:
        utxos_data = utxos_response.json()
        tx_data = tx_response.json()
        
        # Print tx_data for debugging
        print("Transaction Data:", tx_data)
        
        # Determine the format of 'block' and fetch block details if necessary
        block = tx_data.get('block', {})
        if isinstance(block, str):
            # 'block' is a block hash string; fetch block details
            block_details_url = f"{BASE_URL}/blocks/{block}"
            block_response = requests.get(block_details_url, headers=headers)
            if block_response.status_code == 200:
                block_data = block_response.json()
            else:
                print(f"Error fetching block data. Status Code: {block_response.status_code}")
                block_data = {}
        elif isinstance(block, dict):
            # 'block' is already a dictionary with block details
            block_data = block
        else:
            block_data = {}
            print("Unexpected 'block' field format.")
        
        return utxos_data, tx_data, block_data
    else:
        print(f"Error fetching transaction data. UTXOs status: {utxos_response.status_code}, Tx status: {tx_response.status_code}")
        return None, None, None

# Process UTXO data to extract inputs and outputs
def process_utxo_data(utxos_data):
    inputs = []
    outputs = []

    # Parse inputs (sources of ADA and tokens)
    for input_data in utxos_data.get('inputs', []):
        # Ensure 'amount' list is not empty
        if input_data.get('amount'):
            ada_amount_str = input_data['amount'][0].get('quantity', '0')
            try:
                ada_amount = int(ada_amount_str) / 1_000_000  # ADA in Lovelace
            except ValueError:
                ada_amount = 0
            address = input_data.get('address', 'Unknown')
            inputs.append((address, ada_amount))

    # Parse outputs (destinations of ADA and tokens)
    for output_data in utxos_data.get('outputs', []):
        if output_data.get('amount'):
            ada_amount_str = output_data['amount'][0].get('quantity', '0')
            try:
                ada_amount = int(ada_amount_str) / 1_000_000  # ADA in Lovelace
            except ValueError:
                ada_amount = 0
            address = output_data.get('address', 'Unknown')
            outputs.append((address, ada_amount))

    return inputs, outputs

# Function to split a long string into multiple lines
def split_string(string, line_length=15):
    return '\n'.join([string[i:i + line_length] for i in range(0, len(string), line_length)])

# Format transaction metadata
def format_transaction_details(tx_data, block_data):
    # Extract 'epoch' from 'block_data'
    epoch = block_data.get('epoch', 'N/A')
    
    # Extract 'slot' from 'block_data'; fallback to top-level 'slot' if needed
    slot = block_data.get('slot', tx_data.get('slot', 'N/A'))
    
    # Extract 'size' from the top-level
    size = tx_data.get('size', 'N/A')
    
    # Correctly access 'fee' instead of 'fees' and handle it as a string
    fee_str = tx_data.get('fee', '0')
    try:
        fee = int(fee_str) / 1_000_000  # Convert Lovelace to ADA
    except ValueError:
        fee = 'N/A'
    
    # Format 'block_time' if available
    if block_data.get('block_time') or tx_data.get('block_time'):
        timestamp = block_data.get('block_time', tx_data.get('block_time'))
        try:
            block_time = datetime.fromtimestamp(timestamp).strftime('%Y.%m.%d - %H.%M.%S')
        except (OSError, OverflowError, ValueError):
            block_time = 'Invalid timestamp'
    else:
        block_time = 'N/A'
    
    return f"Date: {block_time}\nEpoch: {epoch}, Slot: {slot}\nSize: {size} bytes, Fee: {fee} ADA"

# Create a Cytoscape graph layout with full addresses
def create_cytoscape_elements(tx_id, inputs, outputs, tx_details):
    # List to store the nodes and edges (elements)
    elements = []
    
    # Add the transaction node with details, split into multiple lines
    tx_label = f"Transaction ID:\n{split_string(tx_id, line_length=20)}\n{tx_details}"
    elements.append({
        'data': {'id': tx_id, 'label': tx_label},
        'position': {'x': 300, 'y': 300},
        'classes': 'transaction'
    })
    
    # Determine dynamic spacing based on number of inputs and outputs
    input_start_y = 100
    input_spacing = 100
    output_start_y = 100
    output_spacing = 100
    
    # Add input nodes and edges with split addresses
    for idx, (address, ada_amount) in enumerate(inputs):
        addr_label = f"{split_string(address, line_length=20)}\n({ada_amount:.6f} ADA)"  # Split address into multiple lines
        elements.append({
            'data': {'id': f'input_{idx}', 'label': addr_label},
            'position': {'x': 100, 'y': input_start_y + (idx * input_spacing)},
            'classes': 'input'
        })
        elements.append({
            'data': {'source': f'input_{idx}', 'target': tx_id, 'label': f'{ada_amount:.6f} ADA'},
        })
    
    # Add output nodes and edges with split addresses
    for idx, (address, ada_amount) in enumerate(outputs):
        addr_label = f"{split_string(address, line_length=20)}\n({ada_amount:.6f} ADA)"  # Split address into multiple lines
        elements.append({
            'data': {'id': f'output_{idx}', 'label': addr_label},
            'position': {'x': 500, 'y': output_start_y + (idx * output_spacing)},
            'classes': 'output'
        })
        elements.append({
            'data': {'source': tx_id, 'target': f'output_{idx}', 'label': f'{ada_amount:.6f} ADA'},
        })
    
    return elements

# Dash app
app = dash.Dash(__name__)

# Fetch and process transaction data
tx_id = "847b4f3ad3285aaf77398d6374ff4a80d76fad71795fd1d3aee68604d5921c86"  # Replace with your transaction ID
utxos_data, tx_data, block_data = fetch_transaction_data(tx_id)

if utxos_data and tx_data:
    inputs, outputs = process_utxo_data(utxos_data)
    tx_details = format_transaction_details(tx_data, block_data)
    elements = create_cytoscape_elements(tx_id, inputs, outputs, tx_details)

    # App layout
    app.layout = html.Div([
        cyto.Cytoscape(
            id='cytoscape',
            layout={'name': 'preset'},  # Layout is preset to the given positions
            style={'width': '100%', 'height': '900px'},
            elements=elements,
            stylesheet=[
                {
                    'selector': '.transaction',
                    'style': {
                        'background-color': 'orange',
                        'label': 'data(label)',
                        'text-wrap': 'wrap',
                        'width': 'label',
                        'font-size': '10px',
                        'text-valign': 'center',
                        'text-halign': 'center',
                        'shape': 'ellipse'
                    }
                },
                {
                    'selector': '.input',
                    'style': {
                        'background-color': 'lightgreen',
                        'label': 'data(label)',
                        'text-wrap': 'wrap',
                        'width': 'label',
                        'font-size': '10px',
                        'text-valign': 'center',
                        'text-halign': 'center',
                        'shape': 'ellipse'
                    }
                },
                {
                    'selector': '.output',
                    'style': {
                        'background-color': 'lightcoral',
                        'label': 'data(label)',
                        'text-wrap': 'wrap',
                        'width': 'label',
                        'font-size': '10px',
                        'text-valign': 'center',
                        'text-halign': 'center',
                        'shape': 'ellipse'
                    }
                },
                {
                    'selector': 'edge',
                    'style': {
                        'curve-style': 'bezier',
                        'label': 'data(label)',
                        'font-size': '10px',
                        'target-arrow-shape': 'triangle',
                        'arrow-scale': 1,
                        'line-color': '#9dbaea',
                        'target-arrow-color': '#9dbaea',
                        'color': '#000000',
                        'text-background-color': '#ffffff',
                        'text-background-opacity': 1,
                        'text-background-padding': 2,
                        'text-rotation': 'autorotate'
                    }
                }
            ]
        )
    ])

    if __name__ == '__main__':
        app.run_server(debug=True)
else:
    print("Failed to retrieve transaction data.")
