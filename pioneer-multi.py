from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account import Account
import threading
import time
import random
from colorama import init, Fore

# Enable unaudited HD Wallet features (optional, depends on your use case)
Account.enable_unaudited_hdwallet_features()

# Function to read API key from file
def read_api_key():
    with open("apikey.txt", "r") as file:
        return file.read().strip()

# Function to read private keys from file
def read_private_keys():
    with open("privatekey.txt", "r") as file:
        return [line.strip() for line in file.readlines()]

# Function to check sender balance
def check_balance(address, web3_instance):
    balance = web3_instance.eth.get_balance(address)
    return balance

# Initialize Web3 and other components
rpc_url = read_api_key()
web3 = Web3(Web3.HTTPProvider(rpc_url))
web3.middleware_onion.inject(geth_poa_middleware, layer=0)

# Read private keys from file
private_keys = read_private_keys()

try:
    # Initialize a list to store sender addresses
    sender_addresses = []

    # Create account objects from private keys and get sender addresses
    for private_key in private_keys:
        sender_account = Account.from_key(private_key)
        sender_address = sender_account.address
        sender_addresses.append(sender_address)

    # Display credits and donation message with color
    print(Fore.GREEN + "===================================================")
    print(Fore.GREEN + "                BOT Pioneer Particle")
    print(Fore.GREEN + "===================================================")
    print(Fore.YELLOW + " Developed by: JerryM")
    print(Fore.YELLOW + " Supported by: WIMIX")
    print(Fore.GREEN + "===================================================")
    print(Fore.CYAN + f" DONATE:{Fore.WHITE}0x6Fc6Ea113f38b7c90FF735A9e70AE24674E75D54")
    print(Fore.GREEN + "===================================================")
    print()

    # Initialize a dictionary to store transaction counts for each sender
    transaction_counts = {sender_address: 0 for sender_address in sender_addresses}

    # Initialize a dictionary to store success/failure status for each sender
    transaction_status = {sender_address: [] for sender_address in sender_addresses}

    # Function to handle transaction sending for each sender
    def send_transactions(sender_address, private_key):
        nonlocal transaction_counts
        nonlocal transaction_status

        try:
            while transaction_counts[sender_address] < 50:  # Send 50 transactions per sender
                # Get the latest nonce for sender address
                nonce = web3.eth.get_transaction_count(sender_address)

                # Generate a new random receiver account
                receiver_account = Account.create()
                receiver_address = receiver_account.address
                print(Fore.WHITE + f'Generated address {transaction_counts[sender_address] + 1}:', Fore.WHITE + receiver_address)

                # Amount to send in Ether (random between 0.00001 and 0.000025 ETH)
                amount_to_send = random.uniform(0.000010, 0.000025)

                # Convert amount to wei with proper precision
                amount_to_send_wei = int(web3.to_wei(amount_to_send, 'ether'))

                # Gas Price in gwei (random between 9 and 15 gwei)
                gas_price_gwei = random.uniform(9, 15)
                gas_price_wei = web3.to_wei(gas_price_gwei, 'gwei')

                # Prepare transaction
                transaction = {
                    'nonce': nonce,
                    'to': receiver_address,
                    'value': amount_to_send_wei,
                    'gas': 21000,  # Gas limit for a regular transaction
                    'gasPrice': gas_price_wei,
                    'chainId': 11155111  # Mainnet chain ID
                }

                # Sign the transaction with sender's private key
                signed_txn = web3.eth.account.sign_transaction(transaction, private_key)

                # Send the transaction
                tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)

                # Print transaction details immediately after sending
                print(Fore.WHITE + "Transaction Hash:", Fore.WHITE + web3.to_hex(tx_hash))
                print(Fore.WHITE + "Sender Address:", Fore.GREEN + sender_address)
                print(Fore.WHITE + "Receiver Address:", receiver_address)

                # Increment transaction count
                transaction_counts[sender_address] += 1

                # Wait for 15 seconds before checking transaction status
                time.sleep(15)

                # Retry 5 times with 10-second interval if transaction receipt not found
                retry_count = 0
                while retry_count < 5:
                    try:
                        tx_receipt = web3.eth.get_transaction_receipt(tx_hash)
                        if tx_receipt is not None:
                            if tx_receipt['status'] == 1:
                                print(Fore.GREEN + "Transaksi SUKSES")
                                transaction_status[sender_address].append("SUCCESS")
                                break
                            else:
                                print(Fore.RED + "Transaksi GAGAL")
                                transaction_status[sender_address].append("FAILED")
                                break
                        else:
                            print(Fore.YELLOW + "Transaction is still pending. Retrying...")
                            retry_count += 1
                            time.sleep(10)
                    except Exception as e:
                        print(Fore.RED + f"Error checking transaction status: {str(e)}")
                        retry_count += 1
                        time.sleep(10)

                print()  # Print a blank line for separation

        except ValueError:
            print(Fore.RED + f"Private key yang dimasukkan tidak valid untuk alamat: {sender_address}")

    # Start threads for each sender to send transactions
    sender_threads = []
    for i, sender_address in enumerate(sender_addresses):
        sender_thread = threading.Thread(target=send_transactions, args=(sender_address, private_keys[i]), daemon=True)
        sender_threads.append(sender_thread)
        sender_thread.start()

    # Wait for all threads to complete
    for sender_thread in sender_threads:
        sender_thread.join()

    # Finished sending transactions for all senders
    print(Fore.GREEN + "Selesai.")
    print(Fore.WHITE + f"Berhasil mengirim (50 transaksi) untuk address:", end=" ")
    print(Fore.GREEN + ", ".join(sender_addresses))

except Exception as e:
    print(Fore.RED + f"Terjadi kesalahan: {str(e)}")
