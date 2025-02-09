import csv
import requests
import pandas as pd
from web3 import Web3

# Connect to Ethereum node (Infura or local node)
infura_url = "https://mainnet.infura.io/v3/b26d13039cf344948811e544d795920b"  # Replace with your Infura project ID
web3 = Web3(Web3.HTTPProvider(infura_url))

# Etherscan API key
ETHERSCAN_API_KEY = "DU4KBCQRUKAYTPW2EF6TUQ9MM3BCG2UHUZ"  # Replace with your Etherscan API key

# Check Infura connection
if not web3.is_connected():
    raise Exception("Failed to connect to Ethereum node. Check your Infura project ID and internet connection.")

# Function to get wallet balance
def get_balance(address):
    try:
        balance_wei = web3.eth.get_balance(address)
        return web3.from_wei(balance_wei, 'ether')
    except Exception as e:
        print(f"Error fetching balance for address {address}: {e}")
        return 0

# Function to get transaction count
def get_transaction_count(address):
    try:
        return web3.eth.get_transaction_count(address)
    except Exception as e:
        print(f"Error fetching transaction count for address {address}: {e}")
        return 0

# Function to get transaction details from Etherscan
def get_transactions(address):
    try:
        url = f"https://api.etherscan.io/api?module=account&action=txlist&address={address}&startblock=0&endblock=99999999&sort=asc&apikey={ETHERSCAN_API_KEY}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()['result']
        else:
            print(f"Etherscan API error for address {address}: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error fetching transactions for address {address}: {e}")
        return []

# Function to calculate average transaction value
def calculate_avg_tx_value(transactions, address):
    total_value = 0
    count = 0
    for tx in transactions:
        if tx['from'].lower() == address.lower() or tx['to'].lower() == address.lower():
            value = int(tx['value']) / 1e18  # Convert from wei to ether
            total_value += value
            count += 1
    return total_value / count if count > 0 else 0

# Function to find the largest transaction
def find_largest_transaction(transactions, address):
    largest_value = 0
    for tx in transactions:
        if tx['from'].lower() == address.lower() or tx['to'].lower() == address.lower():
            value = int(tx['value']) / 1e18  # Convert from wei to ether
            if value > largest_value:
                largest_value = value
    return largest_value

# Function to count failed transactions
def count_failed_transactions(transactions, address):
    failed_count = 0
    for tx in transactions:
        if tx['from'].lower() == address.lower() and tx['isError'] == '1':
            failed_count += 1
    return failed_count

# Function to check DeFi staking (placeholder, requires DeFi protocol integration)
def check_defi_staking(address):
    # Placeholder function, integrate with DeFi protocols like Aave, Compound, etc.
    return "Not implemented"

# Main function to process CSV file
def process_wallet_csv(file_path):
    wallets = []
    with open(file_path, mode='r') as file:
        csv_reader = csv.reader(file)
        i = 0
        for row in csv_reader:
            i += 1
            if (i % 10) == 0:
                print(i)
            address = row[0].strip()  # Assuming one address per line
            if not web3.is_address(address):
                print(f"Invalid Ethereum address: {address}")
                continue

            balance = get_balance(address)
            num_transactions = get_transaction_count(address)
            transactions = get_transactions(address)
            avg_tx_value = calculate_avg_tx_value(transactions, address)
            largest_tx = find_largest_transaction(transactions, address)
            failed_tx = count_failed_transactions(transactions, address)
            defi_staking = check_defi_staking(address)

            wallet_data = {
                'address': address,
                'balance': balance,
                'num_transactions': num_transactions,
                'avg_tx_value': avg_tx_value,
                'largest_transaction': largest_tx,
                'failed_transactions': failed_tx,
                'defi_staking': defi_staking
            }
            wallets.append(wallet_data)

    # Convert to DataFrame and save to CSV
    df = pd.DataFrame(wallets)
    df.to_csv('wallet_analysis.csv', index=False)
    print("Wallet analysis saved to 'wallet_analysis.csv'")

# Run the program
if __name__ == "__main__":
    csv_file_path = "wallet_addresses.csv"
    process_wallet_csv(csv_file_path)