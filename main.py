import requests
import pandas as pd
from web3 import Web3
import joblib

# Connect to Ethereum node (Infura or local node)
infura_url = "https://mainnet.infura.io/v3/b26d13039cf344948811e544d795920b"
web3 = Web3(Web3.HTTPProvider(infura_url))

# Etherscan API key
ETHERSCAN_API_KEY = "DU4KBCQRUKAYTPW2EF6TUQ9MM3BCG2UHUZ" 

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

# Function to load ML models and predict anomalies
def predict_anomalies(data):
    # Load the pre-trained models
    isolation_forest = joblib.load("isolation_forest.pkl")
    local_outlier_factor = joblib.load("local_outlier_factor.pkl")
    one_class_svm = joblib.load("one_class_svm.pkl")

    # Predict anomalies
    isolation_forest_result = isolation_forest.predict(data)
    local_outlier_factor_result = local_outlier_factor.predict(data)
    one_class_svm_result = one_class_svm.predict(data)

    return {
        "Isolation Forest": "Anomaly" if isolation_forest_result[0] == -1 else "Normal",
        "Local Outlier Factor": "Anomaly" if local_outlier_factor_result[0] == -1 else "Normal",
        "One-Class SVM": "Anomaly" if one_class_svm_result[0] == -1 else "Normal",
    }

def main(address):
    # Convert address to checksum format
    address = web3.to_checksum_address(address)
    
    # Validate address
    if not web3.is_address(address):
        print("Invalid Ethereum address.")
        return
    
    # Fetch wallet data
    balance = get_balance(address)
    num_transactions = get_transaction_count(address)
    transactions = get_transactions(address)
    avg_tx_value = calculate_avg_tx_value(transactions, address)
    largest_tx = find_largest_transaction(transactions, address)
    failed_tx = count_failed_transactions(transactions, address)
    
    # Prepare data for ML models
    wallet_data = pd.DataFrame({
        'balance': [balance],
        'num_transactions': [num_transactions],
        'avg_tx_value': [avg_tx_value],
        'largest_transaction': [largest_tx],
        'failed_transactions': [failed_tx],
    })
    
    # Predict anomalies
    anomaly_results = predict_anomalies(wallet_data)
    
    n = 0
    count = 0
    ans = ""
    outs=[]
    for model, result in anomaly_results.items():
        outs.append(result)
        if result == "Normal":
            n += 1
        count += 1
        ans += model + " Prediction: " + result + "   "
        print(ans)
    ans += "Overall result: " + str(n) + "/" + str(count)
    outs.append(str(n))
    return outs[0],outs[1],outs[2],outs[3]
    return (ans)

if __name__ == "__main__":
    address = input("Enter your wallet address: ").strip()
    print(main(address))
    