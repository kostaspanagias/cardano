# About
A repository of useful scripts for the cardano community. Work in progress...


## Prerequisites
I use Blockfrost API to explore the Cardano Blockchain.  
Get your API Key at: https://blockfrost.io/ (free tier available)

# Files

### token_holders_v4.py
This python script fetches all the holders of a particular native token in cardano blockchain. You need to have the token **Encoded Name** in order to run it. You can use popular Cardano Explorers (e.g. https://cexplorer.io/) to get the encoded name of the token you are interested in and remove the dot [.] </br>For example ticker: *IAG* is: *5d16cc1a177b5d9ba9cfa9793b07e60f1fb70fea1f8aef064415d114494147*, etc.
#### Dependencies
* **Pandas**. How to install: `pip install pandas`
* **Openpyxl**. How to install: `pip install openpyxl`
* **Dotenv**. How to install: `pip install python-dotenv`
