# About
A repository of useful Python scripts for the cardano community. Each script is a subfolder in folder `code`.

*This is a work in progress...*


## Prerequisites
I use Blockfrost API to explore the Cardano Blockchain.  
Get your API Key at: https://blockfrost.io/ (free tier available)



# List of Scripts

### token_holders v.4 (file: [token_holders.py](code/token_holders/token_holders.py))
This python script fetches all the holders of a particular native token in cardano blockchain and saves this info to a local excel file. You need to have the token **Encoded Name** in order to run it.

You can use popular Cardano Explorers (e.g. https://cexplorer.io/) to get the encoded name of the token you are interested in and remove the dot [.] </br>For example ticker: *IAG* is: *5d16cc1a177b5d9ba9cfa9793b07e60f1fb70fea1f8aef064415d114494147*, etc.

#### Dependencies
* **Pandas**. How to install: `pip install pandas`
* **Openpyxl**. How to install: `pip install openpyxl`
* **Dotenv**. How to install: `pip install python-dotenv`
* **requests**. How to install: `pip install requests`

---

### stake_addresses (file: [stake_addresses_v2.py](code/stake_addresses/stake_addresses.py))
This script will read a csv file with a list of stake keys and get all the addresses of each stake key exported into an Excel file for further analysis. A sample file **stake.csv** is included in the repository for you to use as template.
#### Dependencies
* **Pandas**. How to install: `pip install pandas`
* **Dotenv**. How to install: `pip install python-dotenv`
* **requests**. How to install: `pip install requests`

---

### single_transactions (file: [single_transaction.py](code/transaction/single_transaction.py))
This script asks for a transaction id and it outputs and excel with inputs & outputs (UTXOs) - SheetName: "ADA_Transcations" and native tokens that moved wallets - SheetName: "Token Transactions". The excel is saved with the transaction id as its name.
#### Dependencies
* **Pandas**. How to install: `pip install pandas`
* **Dotenv**. How to install: `pip install python-dotenv`
* **requests**. How to install: `pip install requests`

---

### transaction_vizualization-v2 (file: [transaction_vizualization.py](code/transaction/transaction_vizualization-v2.py))
This script visualizes the flow of assets in a Cardano transaction using Dash Cytoscape. It fetches transaction data (inputs, outputs, ADA amounts, and metadata) from the Blockfrost API and displays an interactive graph where each node represents a wallet or transaction.
#### Dependencies
* **Dotenv**. How to install: `pip install python-dotenv`
* **requests**. How to install: `pip install requests`
* **dash**. How to install: `pip install dash`
* **dash-cytoscape**. How to install: `pip install dash-cytoscape`

### Screenshot:</br>
<img src="files/transaction_visualization.jpg" alt="Screenshot of transaction_vizualization-v2 output" style="width: 70%;" />
