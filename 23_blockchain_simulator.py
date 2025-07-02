import hashlib
import time
import json
import threading
import random
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import base64
import os
import pickle
from collections import defaultdict, OrderedDict
from datetime import datetime
import socket
import uuid
import ecdsa

# Constants
MINING_DIFFICULTY = 4  # Number of leading zeros required in hash
MINING_REWARD = 50     # Reward for mining a block
HALVING_INTERVAL = 10  # Number of blocks before reward is halved
BLOCK_SIZE_LIMIT = 1024 * 1024  # 1MB max block size
INITIAL_COINS = 21000000  # Total number of coins in circulation
MAX_TRANSACTIONS_PER_BLOCK = 100

class Transaction:
    """Represents a cryptocurrency transaction in the blockchain"""
    
    def __init__(self, sender, recipient, amount, fee=0, timestamp=None, signature=None):
        self.sender = sender  # Public key of sender
        self.recipient = recipient  # Public key of recipient
        self.amount = amount  # Amount to transfer
        self.fee = fee  # Transaction fee
        self.timestamp = timestamp if timestamp else time.time()
        self.transaction_id = None  # Will be set when added to mempool
        self.signature = signature  # Digital signature
        
    def calculate_hash(self):
        """Calculate the hash of the transaction"""
        transaction_string = f"{self.sender}{self.recipient}{self.amount}{self.fee}{self.timestamp}"
        return hashlib.sha256(transaction_string.encode()).hexdigest()
    
    def sign_transaction(self, private_key):
        """Sign the transaction with the sender's private key"""
        if not private_key:
            raise Exception("No private key provided")
            
        transaction_hash = self.calculate_hash()
        sk = ecdsa.SigningKey.from_string(base64.b64decode(private_key), curve=ecdsa.SECP256k1)
        self.signature = base64.b64encode(sk.sign(transaction_hash.encode())).decode()
        return self.signature
    
    def verify_signature(self):
        """Verify the transaction signature"""
        if self.sender == "COINBASE":  # Mining reward transaction
            return True
            
        if not self.signature:
            return False
            
        try:
            transaction_hash = self.calculate_hash()
            vk = ecdsa.VerifyingKey.from_string(base64.b64decode(self.sender), curve=ecdsa.SECP256k1)
            return vk.verify(base64.b64decode(self.signature), transaction_hash.encode())
        except:
            return False
    
    def to_dict(self):
        """Convert transaction to dictionary for JSON serialization"""
        return {
            "sender": self.sender,
            "recipient": self.recipient,
            "amount": self.amount,
            "fee": self.fee,
            "timestamp": self.timestamp,
            "transaction_id": self.transaction_id,
            "signature": self.signature
        }
    
    @classmethod
    def from_dict(cls, transaction_dict):
        """Create a transaction from a dictionary"""
        transaction = cls(
            transaction_dict["sender"],
            transaction_dict["recipient"],
            transaction_dict["amount"],
            transaction_dict["fee"],
            transaction_dict["timestamp"],
            transaction_dict["signature"]
        )
        transaction.transaction_id = transaction_dict["transaction_id"]
        return transaction
        
    def __str__(self):
        return f"Transaction(ID: {self.transaction_id[:8]}..., From: {self.sender[:8]}..., To: {self.recipient[:8]}..., Amount: {self.amount}, Fee: {self.fee})"

class Block:
    """Represents a block in the blockchain"""
    
    def __init__(self, index, transactions, timestamp, previous_hash, nonce=0):
        self.index = index  # Block number
        self.transactions = transactions  # List of transactions
        self.timestamp = timestamp  # Time of creation
        self.previous_hash = previous_hash  # Hash of previous block
        self.nonce = nonce  # Nonce for mining
        self.merkle_root = self.calculate_merkle_root()  # Merkle root of transactions
        self.hash = self.calculate_hash()  # Hash of this block
        
    def calculate_hash(self):
        """Calculate the hash of the block"""
        block_string = f"{self.index}{self.timestamp}{self.previous_hash}{self.merkle_root}{self.nonce}"
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def calculate_merkle_root(self):
        """Calculate the Merkle root of the transactions"""
        if not self.transactions:
            return hashlib.sha256("".encode()).hexdigest()
            
        transaction_hashes = [t.calculate_hash() for t in self.transactions]
        
        # If odd number of transactions, duplicate the last one
        if len(transaction_hashes) % 2 != 0:
            transaction_hashes.append(transaction_hashes[-1])
            
        # Build the Merkle tree
        while len(transaction_hashes) > 1:
            new_hashes = []
            for i in range(0, len(transaction_hashes), 2):
                combined = transaction_hashes[i] + transaction_hashes[i+1]
                new_hash = hashlib.sha256(combined.encode()).hexdigest()
                new_hashes.append(new_hash)
            transaction_hashes = new_hashes
            
            # If odd number of hashes, duplicate the last one
            if len(transaction_hashes) % 2 != 0 and len(transaction_hashes) > 1:
                transaction_hashes.append(transaction_hashes[-1])
                
        return transaction_hashes[0]
    
    def mine_block(self, difficulty):
        """Mine the block by finding a hash with the required difficulty"""
        target = "0" * difficulty
        
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()
            
        return self.hash
    
    def validate_transactions(self, blockchain):
        """Validate all transactions in the block"""
        # Check for duplicate transactions
        transaction_ids = set()
        for transaction in self.transactions:
            if transaction.transaction_id in transaction_ids:
                return False
            transaction_ids.add(transaction.transaction_id)
            
            # Verify transaction signature
            if not transaction.verify_signature():
                return False
                
            # Skip COINBASE transactions for balance check
            if transaction.sender == "COINBASE":
                continue
                
            # Check if sender has enough balance
            sender_balance = blockchain.get_balance(transaction.sender)
            if sender_balance < transaction.amount + transaction.fee:
                return False
                
        return True
    
    def to_dict(self):
        """Convert block to dictionary for JSON serialization"""
        return {
            "index": self.index,
            "transactions": [t.to_dict() for t in self.transactions],
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "merkle_root": self.merkle_root,
            "hash": self.hash
        }
    
    @classmethod
    def from_dict(cls, block_dict):
        """Create a block from a dictionary"""
        transactions = [Transaction.from_dict(t) for t in block_dict["transactions"]]
        block = cls(
            block_dict["index"],
            transactions,
            block_dict["timestamp"],
            block_dict["previous_hash"],
            block_dict["nonce"]
        )
        block.merkle_root = block_dict["merkle_root"]
        block.hash = block_dict["hash"]
        return block
        
    def __str__(self):
        return f"Block(Index: {self.index}, Hash: {self.hash[:10]}..., Transactions: {len(self.transactions)}, Nonce: {self.nonce})"

class Blockchain:
    """Represents the blockchain with all its functionality"""
    
    def __init__(self):
        self.chain = []  # List of blocks
        self.mempool = []  # Pending transactions
        self.utxo = {}  # Unspent Transaction Outputs
        self.difficulty = MINING_DIFFICULTY
        self.mining_reward = MINING_REWARD
        self.halving_count = 0
        self.nodes = set()  # Network nodes for consensus
        
        # Create the genesis block
        self.create_genesis_block()
        
    def create_genesis_block(self):
        """Create the first block in the blockchain"""
        # Create a coinbase transaction for the genesis block
        coinbase_tx = Transaction("COINBASE", "Genesis", INITIAL_COINS)
        coinbase_tx.transaction_id = "genesis_coinbase_tx"
        
        # Create the genesis block
        genesis_block = Block(0, [coinbase_tx], time.time(), "0")
        genesis_block.hash = genesis_block.calculate_hash()
        
        # Add the genesis block to the chain
        self.chain.append(genesis_block)
        
        # Add the coinbase transaction to the UTXO set
        self.utxo[coinbase_tx.transaction_id] = {
            "recipient": coinbase_tx.recipient,
            "amount": coinbase_tx.amount,
            "spent": False
        }
        
    def get_latest_block(self):
        """Get the latest block in the blockchain"""
        return self.chain[-1]
    
    def add_transaction_to_mempool(self, transaction):
        """Add a transaction to the mempool"""
        # Validate the transaction
        if not transaction.verify_signature():
            return False, "Invalid signature"
            
        # Check if sender has enough balance (except for coinbase transactions)
        if transaction.sender != "COINBASE":
            sender_balance = self.get_balance(transaction.sender)
            if sender_balance < transaction.amount + transaction.fee:
                return False, "Insufficient balance"
        
        # Generate transaction ID if not set
        if not transaction.transaction_id:
            transaction.transaction_id = transaction.calculate_hash()
            
        # Check if transaction is already in mempool
        for tx in self.mempool:
            if tx.transaction_id == transaction.transaction_id:
                return False, "Transaction already in mempool"
                
        # Add to mempool
        self.mempool.append(transaction)
        return True, transaction.transaction_id
    
    def mine_pending_transactions(self, miner_address):
        """Mine pending transactions and add a new block to the chain"""
        # Check if there are any transactions to mine
        if not self.mempool and miner_address != "Genesis":
            return False, "No transactions to mine"
            
        # Create a list of transactions to include in the block
        # Sort by fee (highest fee first)
        transactions_to_mine = sorted(
            self.mempool, 
            key=lambda t: t.fee, 
            reverse=True
        )[:MAX_TRANSACTIONS_PER_BLOCK]
        
        # Create a coinbase transaction (mining reward)
        reward = self.mining_reward
        coinbase_tx = Transaction("COINBASE", miner_address, reward)
        coinbase_tx.transaction_id = f"coinbase_{len(self.chain)}_{time.time()}"
        
        # Add coinbase transaction to the beginning of the list
        transactions_to_mine.insert(0, coinbase_tx)
        
        # Create a new block
        block = Block(
            len(self.chain),
            transactions_to_mine,
            time.time(),
            self.get_latest_block().hash
        )
        
        # Mine the block
        block.mine_block(self.difficulty)
        
        # Add the block to the chain
        self.chain.append(block)
        
        # Update UTXO set
        for tx in transactions_to_mine:
            # Add new outputs
            self.utxo[tx.transaction_id] = {
                "recipient": tx.recipient,
                "amount": tx.amount,
                "spent": False
            }
            
            # Mark inputs as spent (except for coinbase)
            if tx.sender != "COINBASE":
                # Find unspent outputs for the sender
                for utxo_id, utxo_data in self.utxo.items():
                    if utxo_data["recipient"] == tx.sender and not utxo_data["spent"]:
                        if utxo_data["amount"] >= tx.amount + tx.fee:
                            utxo_data["spent"] = True
                            
                            # Create change UTXO if needed
                            change = utxo_data["amount"] - (tx.amount + tx.fee)
                            if change > 0:
                                change_tx_id = f"change_{tx.transaction_id}"
                                self.utxo[change_tx_id] = {
                                    "recipient": tx.sender,
                                    "amount": change,
                                    "spent": False
                                }
                            break
        
        # Remove mined transactions from mempool
        self.mempool = [tx for tx in self.mempool if tx not in transactions_to_mine[1:]]
        
        # Check if we need to adjust difficulty or halve the reward
        if len(self.chain) % 10 == 0:
            self.adjust_difficulty()
            
        if len(self.chain) % HALVING_INTERVAL == 0:
            self.halving_count += 1
            self.mining_reward = MINING_REWARD / (2 ** self.halving_count)
            
        return True, block
    
    def adjust_difficulty(self):
        """Adjust the mining difficulty based on the mining rate"""
        # In a real blockchain, this would adjust based on the time it takes to mine blocks
        # For simplicity, we'll just increase difficulty every 10 blocks
        if len(self.chain) % 20 == 0:
            self.difficulty += 1
    
    def is_chain_valid(self):
        """Validate the entire blockchain"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            
            # Check if the current block's hash is valid
            if current_block.hash != current_block.calculate_hash():
                return False
                
            # Check if the current block points to the previous block's hash
            if current_block.previous_hash != previous_block.hash:
                return False
                
            # Check if the block's transactions are valid
            if not current_block.validate_transactions(self):
                return False
                
        return True
    
    def get_balance(self, address):
        """Get the balance of an address"""
        balance = 0
        for utxo_id, utxo_data in self.utxo.items():
            if utxo_data["recipient"] == address and not utxo_data["spent"]:
                balance += utxo_data["amount"]
        return balance
    
    def get_transaction_history(self, address):
        """Get the transaction history of an address"""
        history = []
        for block in self.chain:
            for tx in block.transactions:
                if tx.sender == address or tx.recipient == address:
                    history.append({
                        "block": block.index,
                        "transaction_id": tx.transaction_id,
                        "sender": tx.sender,
                        "recipient": tx.recipient,
                        "amount": tx.amount,
                        "fee": tx.fee,
                        "timestamp": tx.timestamp
                    })
        return history
    
    def to_dict(self):
        """Convert blockchain to dictionary for JSON serialization"""
        return {
            "chain": [block.to_dict() for block in self.chain],
            "mempool": [tx.to_dict() for tx in self.mempool],
            "difficulty": self.difficulty,
            "mining_reward": self.mining_reward,
            "halving_count": self.halving_count
        }
    
    @classmethod
    def from_dict(cls, blockchain_dict):
        """Create a blockchain from a dictionary"""
        blockchain = cls()
        blockchain.chain = [Block.from_dict(block_dict) for block_dict in blockchain_dict["chain"]]
        blockchain.mempool = [Transaction.from_dict(tx_dict) for tx_dict in blockchain_dict["mempool"]]
        blockchain.difficulty = blockchain_dict["difficulty"]
        blockchain.mining_reward = blockchain_dict["mining_reward"]
        blockchain.halving_count = blockchain_dict["halving_count"]
        
        # Rebuild UTXO set
        blockchain.utxo = {}
        for block in blockchain.chain:
            for tx in block.transactions:
                blockchain.utxo[tx.transaction_id] = {
                    "recipient": tx.recipient,
                    "amount": tx.amount,
                    "spent": False
                }
                
                # Mark inputs as spent (except for coinbase)
                if tx.sender != "COINBASE":
                    # Find unspent outputs for the sender
                    for utxo_id, utxo_data in list(blockchain.utxo.items()):
                        if utxo_data["recipient"] == tx.sender and not utxo_data["spent"]:
                            if utxo_data["amount"] >= tx.amount + tx.fee:
                                utxo_data["spent"] = True
                                
                                # Create change UTXO if needed
                                change = utxo_data["amount"] - (tx.amount + tx.fee)
                                if change > 0:
                                    change_tx_id = f"change_{tx.transaction_id}"
                                    blockchain.utxo[change_tx_id] = {
                                        "recipient": tx.sender,
                                        "amount": change,
                                        "spent": False
                                    }
                                break
        
        return blockchain

class Wallet:
    """Represents a cryptocurrency wallet"""
    
    def __init__(self, blockchain=None, private_key=None, public_key=None):
        """Initialize a new wallet or load an existing one"""
        self.blockchain = blockchain
        
        if private_key and public_key:
            # Load existing keys
            self.private_key = private_key
            self.public_key = public_key
        else:
            # Generate new keys
            self.generate_keys()
    
    def generate_keys(self):
        """Generate a new key pair"""
        # Generate a new private key
        sk = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
        self.private_key = base64.b64encode(sk.to_string()).decode()
        
        # Derive the public key
        vk = sk.get_verifying_key()
        self.public_key = base64.b64encode(vk.to_string()).decode()
        
    def get_balance(self):
        """Get the wallet balance"""
        if not self.blockchain:
            return 0
        return self.blockchain.get_balance(self.public_key)
    
    def create_transaction(self, recipient, amount, fee=1):
        """Create a new transaction"""
        if not self.blockchain:
            raise Exception("Wallet not connected to blockchain")
            
        # Check balance
        balance = self.get_balance()
        if balance < amount + fee:
            raise Exception(f"Insufficient balance. You have {balance}, but need {amount + fee}")
            
        # Create transaction
        transaction = Transaction(self.public_key, recipient, amount, fee)
        
        # Sign transaction
        transaction.sign_transaction(self.private_key)
        
        return transaction
    
    def send(self, recipient, amount, fee=1):
        """Send coins to another address"""
        if not self.blockchain:
            raise Exception("Wallet not connected to blockchain")
            
        # Create and sign transaction
        transaction = self.create_transaction(recipient, amount, fee)
        
        # Add to mempool
        success, result = self.blockchain.add_transaction_to_mempool(transaction)
        
        if success:
            return True, result  # Result is the transaction ID
        else:
            return False, result  # Result is the error message
    
    def get_transaction_history(self):
        """Get the transaction history for this wallet"""
        if not self.blockchain:
            return []
        return self.blockchain.get_transaction_history(self.public_key)
    
    def to_dict(self):
        """Convert wallet to dictionary for JSON serialization"""
        return {
            "public_key": self.public_key,
            "private_key": self.private_key
        }
    
    @classmethod
    def from_dict(cls, wallet_dict, blockchain=None):
        """Create a wallet from a dictionary"""
        return cls(blockchain, wallet_dict["private_key"], wallet_dict["public_key"])

class BlockchainGUI:
    """GUI for the blockchain simulator"""
    
    def __init__(self, root):
        """Initialize the GUI"""
        self.root = root
        self.root.title("Blockchain Simulator")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)
        
        # Initialize blockchain and wallets
        self.blockchain = Blockchain()
        self.wallets = {}  # Dictionary of wallets (name -> Wallet)
        self.active_wallet = None
        
        # Mining variables
        self.is_mining = False
        self.mining_thread = None
        self.auto_mining = False
        
        # Create UI components
        self.create_menu()
        self.create_main_frame()
        
        # Load saved data if available
        self.load_data()
        
    def create_menu(self):
        """Create the menu bar"""
        menu_bar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="New Blockchain", command=self.new_blockchain)
        file_menu.add_command(label="Save", command=self.save_data)
        file_menu.add_command(label="Load", command=self.load_data)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)
        
        # Wallet menu
        wallet_menu = tk.Menu(menu_bar, tearoff=0)
        wallet_menu.add_command(label="Create New Wallet", command=self.create_wallet_dialog)
        wallet_menu.add_command(label="Import Wallet", command=self.import_wallet_dialog)
        wallet_menu.add_command(label="Export Active Wallet", command=self.export_wallet)
        menu_bar.add_cascade(label="Wallet", menu=wallet_menu)
        
        # Mining menu
        mining_menu = tk.Menu(menu_bar, tearoff=0)
        mining_menu.add_command(label="Start Mining", command=self.start_mining)
        mining_menu.add_command(label="Stop Mining", command=self.stop_mining)
        mining_menu.add_separator()
        
        self.auto_mining_var = tk.BooleanVar()
        mining_menu.add_checkbutton(label="Auto Mining", 
                                   variable=self.auto_mining_var,
                                   command=self.toggle_auto_mining)
        menu_bar.add_cascade(label="Mining", menu=mining_menu)
        
        # Help menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Help", command=self.show_help)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menu_bar)
        
    def create_main_frame(self):
        """Create the main frame with tabs"""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.overview_tab = ttk.Frame(self.notebook)
        self.blockchain_tab = ttk.Frame(self.notebook)
        self.wallet_tab = ttk.Frame(self.notebook)
        self.transactions_tab = ttk.Frame(self.notebook)
        self.mining_tab = ttk.Frame(self.notebook)
        self.network_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.overview_tab, text="Overview")
        self.notebook.add(self.blockchain_tab, text="Blockchain")
        self.notebook.add(self.wallet_tab, text="Wallet")
        self.notebook.add(self.transactions_tab, text="Transactions")
        self.notebook.add(self.mining_tab, text="Mining")
        self.notebook.add(self.network_tab, text="Network")
        
        # Create content for each tab
        self.create_overview_tab()
        self.create_blockchain_tab()
        self.create_wallet_tab()
        self.create_transactions_tab()
        self.create_mining_tab()
        self.create_network_tab()
        
        # Create status bar
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = ttk.Label(self.status_bar, text="Ready")
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        self.mining_status = ttk.Label(self.status_bar, text="Mining: Inactive")
        self.mining_status.pack(side=tk.RIGHT, padx=10)
        
    def create_overview_tab(self):
        """Create the overview tab"""
        # Left frame for blockchain info
        left_frame = ttk.LabelFrame(self.overview_tab, text="Blockchain Information")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Blockchain stats
        stats_frame = ttk.Frame(left_frame)
        stats_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(stats_frame, text="Blockchain Height:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.height_label = ttk.Label(stats_frame, text="0")
        self.height_label.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(stats_frame, text="Difficulty:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.difficulty_label = ttk.Label(stats_frame, text=str(MINING_DIFFICULTY))
        self.difficulty_label.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(stats_frame, text="Mining Reward:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.reward_label = ttk.Label(stats_frame, text=str(MINING_REWARD))
        self.reward_label.grid(row=2, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(stats_frame, text="Pending Transactions:").grid(row=3, column=0, sticky="w", padx=5, pady=2)
        self.pending_label = ttk.Label(stats_frame, text="0")
        self.pending_label.grid(row=3, column=1, sticky="w", padx=5, pady=2)
        
        # Recent blocks
        blocks_frame = ttk.LabelFrame(left_frame, text="Recent Blocks")
        blocks_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.blocks_tree = ttk.Treeview(blocks_frame, columns=("Index", "Hash", "Transactions", "Time"))
        self.blocks_tree.heading("Index", text="Index")
        self.blocks_tree.heading("Hash", text="Hash")
        self.blocks_tree.heading("Transactions", text="Transactions")
        self.blocks_tree.heading("Time", text="Time")
        
        self.blocks_tree.column("#0", width=0, stretch=tk.NO)
        self.blocks_tree.column("Index", width=50, anchor=tk.CENTER)
        self.blocks_tree.column("Hash", width=200)
        self.blocks_tree.column("Transactions", width=100, anchor=tk.CENTER)
        self.blocks_tree.column("Time", width=150)
        
        self.blocks_tree.pack(fill=tk.BOTH, expand=True)
        self.blocks_tree.bind("<Double-1>", self.show_block_details)
        
        # Right frame for wallet info
        right_frame = ttk.LabelFrame(self.overview_tab, text="Wallet Information")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Wallet selector
        wallet_frame = ttk.Frame(right_frame)
        wallet_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(wallet_frame, text="Active Wallet:").pack(side=tk.LEFT, padx=5)
        
        self.wallet_var = tk.StringVar()
        self.wallet_combo = ttk.Combobox(wallet_frame, textvariable=self.wallet_var, state="readonly")
        self.wallet_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.wallet_combo.bind("<<ComboboxSelected>>", self.change_wallet)
        
        # Wallet stats
        wallet_stats = ttk.Frame(right_frame)
        wallet_stats.pack(fill=tk.X, pady=10)
        
        ttk.Label(wallet_stats, text="Balance:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.balance_label = ttk.Label(wallet_stats, text="0")
        self.balance_label.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(wallet_stats, text="Address:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.address_label = ttk.Label(wallet_stats, text="-")
        self.address_label.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        
        # Transaction history
        tx_frame = ttk.LabelFrame(right_frame, text="Recent Transactions")
        tx_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.tx_tree = ttk.Treeview(tx_frame, columns=("ID", "From", "To", "Amount", "Time"))
        self.tx_tree.heading("ID", text="ID")
        self.tx_tree.heading("From", text="From")
        self.tx_tree.heading("To", text="To")
        self.tx_tree.heading("Amount", text="Amount")
        self.tx_tree.heading("Time", text="Time")
        
        self.tx_tree.column("#0", width=0, stretch=tk.NO)
        self.tx_tree.column("ID", width=80)
        self.tx_tree.column("From", width=100)
        self.tx_tree.column("To", width=100)
        self.tx_tree.column("Amount", width=80, anchor=tk.E)
        self.tx_tree.column("Time", width=150)
        
        self.tx_tree.pack(fill=tk.BOTH, expand=True)
        self.tx_tree.bind("<Double-1>", self.show_transaction_details)
        
    def create_blockchain_tab(self):
        """Create the blockchain tab"""
        # Top frame for controls
        top_frame = ttk.Frame(self.blockchain_tab)
        top_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(top_frame, text="Refresh", command=self.refresh_blockchain).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="Validate Chain", command=self.validate_blockchain).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="Export Blockchain", command=self.export_blockchain).pack(side=tk.LEFT, padx=5)
        
        # Blockchain explorer
        explorer_frame = ttk.LabelFrame(self.blockchain_tab, text="Blockchain Explorer")
        explorer_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create a tree view for the blockchain
        self.blockchain_tree = ttk.Treeview(explorer_frame, columns=("Index", "Hash", "Prev Hash", "Transactions", "Time", "Nonce"))
        self.blockchain_tree.heading("Index", text="Index")
        self.blockchain_tree.heading("Hash", text="Hash")
        self.blockchain_tree.heading("Prev Hash", text="Previous Hash")
        self.blockchain_tree.heading("Transactions", text="Transactions")
        self.blockchain_tree.heading("Time", text="Timestamp")
        self.blockchain_tree.heading("Nonce", text="Nonce")
        
        self.blockchain_tree.column("#0", width=0, stretch=tk.NO)
        self.blockchain_tree.column("Index", width=50, anchor=tk.CENTER)
        self.blockchain_tree.column("Hash", width=200)
        self.blockchain_tree.column("Prev Hash", width=200)
        self.blockchain_tree.column("Transactions", width=100, anchor=tk.CENTER)
        self.blockchain_tree.column("Time", width=150)
        self.blockchain_tree.column("Nonce", width=100, anchor=tk.CENTER)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(explorer_frame, orient="vertical", command=self.blockchain_tree.yview)
        self.blockchain_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.blockchain_tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind double-click event
        self.blockchain_tree.bind("<Double-1>", self.show_block_details)
        
        # Block details frame
        details_frame = ttk.LabelFrame(self.blockchain_tab, text="Block Details")
        details_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create a text widget for block details
        self.block_details_text = scrolledtext.ScrolledText(details_frame, height=10)
        self.block_details_text.pack(fill=tk.BOTH, expand=True)
        
    def create_wallet_tab(self):
        """Create the wallet tab"""
        # Left frame for wallet list and creation
        left_frame = ttk.LabelFrame(self.wallet_tab, text="Wallets")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Wallet controls
        controls_frame = ttk.Frame(left_frame)
        controls_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(controls_frame, text="Create New Wallet", command=self.create_wallet_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Import Wallet", command=self.import_wallet_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Export Wallet", command=self.export_wallet).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Delete Wallet", command=self.delete_wallet).pack(side=tk.LEFT, padx=5)
        
        # Wallet list
        wallet_list_frame = ttk.Frame(left_frame)
        wallet_list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.wallet_listbox = tk.Listbox(wallet_list_frame, selectmode=tk.SINGLE)
        self.wallet_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.wallet_listbox.bind("<<ListboxSelect>>", self.select_wallet_from_list)
        
        wallet_scrollbar = ttk.Scrollbar(wallet_list_frame, orient="vertical", command=self.wallet_listbox.yview)
        self.wallet_listbox.configure(yscroll=wallet_scrollbar.set)
        wallet_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Right frame for wallet details and actions
        right_frame = ttk.LabelFrame(self.wallet_tab, text="Wallet Details")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Wallet info
        info_frame = ttk.Frame(right_frame)
        info_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(info_frame, text="Name:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.wallet_name_label = ttk.Label(info_frame, text="-")
        self.wallet_name_label.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(info_frame, text="Address:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.wallet_address_label = ttk.Label(info_frame, text="-")
        self.wallet_address_label.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(info_frame, text="Balance:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.wallet_balance_label = ttk.Label(info_frame, text="0")
        self.wallet_balance_label.grid(row=2, column=1, sticky="w", padx=5, pady=2)
        
        # Send coins frame
        send_frame = ttk.LabelFrame(right_frame, text="Send Coins")
        send_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(send_frame, text="Recipient:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.recipient_entry = ttk.Entry(send_frame, width=50)
        self.recipient_entry.grid(row=0, column=1, sticky="we", padx=5, pady=5)
        
        ttk.Label(send_frame, text="Amount:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.amount_entry = ttk.Entry(send_frame, width=20)
        self.amount_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(send_frame, text="Fee:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.fee_entry = ttk.Entry(send_frame, width=20)
        self.fee_entry.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        self.fee_entry.insert(0, "1")  # Default fee
        
        ttk.Button(send_frame, text="Send", command=self.send_transaction).grid(row=3, column=1, sticky="w", padx=5, pady=10)
        
        # Transaction history
        history_frame = ttk.LabelFrame(right_frame, text="Transaction History")
        history_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.wallet_tx_tree = ttk.Treeview(history_frame, columns=("ID", "Type", "Address", "Amount", "Time"))
        self.wallet_tx_tree.heading("ID", text="ID")
        self.wallet_tx_tree.heading("Type", text="Type")
        self.wallet_tx_tree.heading("Address", text="Address")
        self.wallet_tx_tree.heading("Amount", text="Amount")
        self.wallet_tx_tree.heading("Time", text="Time")
        
        self.wallet_tx_tree.column("#0", width=0, stretch=tk.NO)
        self.wallet_tx_tree.column("ID", width=80)
        self.wallet_tx_tree.column("Type", width=80, anchor=tk.CENTER)
        self.wallet_tx_tree.column("Address", width=200)
        self.wallet_tx_tree.column("Amount", width=100, anchor=tk.E)
        self.wallet_tx_tree.column("Time", width=150)
        
        self.wallet_tx_tree.pack(fill=tk.BOTH, expand=True)
        
    def create_transactions_tab(self):
        """Create the transactions tab"""
        # Top frame for controls
        top_frame = ttk.Frame(self.transactions_tab)
        top_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(top_frame, text="Refresh", command=self.refresh_transactions).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="Create Transaction", command=self.create_transaction_dialog).pack(side=tk.LEFT, padx=5)
        
        # Mempool frame
        mempool_frame = ttk.LabelFrame(self.transactions_tab, text="Transaction Mempool")
        mempool_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.mempool_tree = ttk.Treeview(mempool_frame, columns=("ID", "From", "To", "Amount", "Fee", "Time"))
        self.mempool_tree.heading("ID", text="ID")
        self.mempool_tree.heading("From", text="From")
        self.mempool_tree.heading("To", text="To")
        self.mempool_tree.heading("Amount", text="Amount")
        self.mempool_tree.heading("Fee", text="Fee")
        self.mempool_tree.heading("Time", text="Time")
        
        self.mempool_tree.column("#0", width=0, stretch=tk.NO)
        self.mempool_tree.column("ID", width=80)
        self.mempool_tree.column("From", width=150)
        self.mempool_tree.column("To", width=150)
        self.mempool_tree.column("Amount", width=100, anchor=tk.E)
        self.mempool_tree.column("Fee", width=80, anchor=tk.E)
        self.mempool_tree.column("Time", width=150)
        
        self.mempool_tree.pack(fill=tk.BOTH, expand=True)
        self.mempool_tree.bind("<Double-1>", self.show_transaction_details)
        
        # Transaction details frame
        details_frame = ttk.LabelFrame(self.transactions_tab, text="Transaction Details")
        details_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.tx_details_text = scrolledtext.ScrolledText(details_frame, height=10)
        self.tx_details_text.pack(fill=tk.BOTH, expand=True)
        
    def create_mining_tab(self):
        """Create the mining tab"""
        # Top frame for controls
        top_frame = ttk.Frame(self.mining_tab)
        top_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(top_frame, text="Start Mining", command=self.start_mining).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="Stop Mining", command=self.stop_mining).pack(side=tk.LEFT, padx=5)
        
        # Auto mining checkbox
        self.auto_mining_check = ttk.Checkbutton(
            top_frame, 
            text="Auto Mining", 
            variable=self.auto_mining_var,
            command=self.toggle_auto_mining
        )
        self.auto_mining_check.pack(side=tk.LEFT, padx=20)
        
        # Mining settings frame
        settings_frame = ttk.LabelFrame(self.mining_tab, text="Mining Settings")
        settings_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(settings_frame, text="Miner Address:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        self.miner_var = tk.StringVar()
        self.miner_combo = ttk.Combobox(settings_frame, textvariable=self.miner_var, state="readonly", width=50)
        self.miner_combo.grid(row=0, column=1, sticky="we", padx=5, pady=5)
        
        ttk.Label(settings_frame, text="Difficulty:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        
        self.difficulty_var = tk.IntVar(value=MINING_DIFFICULTY)
        difficulty_spinbox = ttk.Spinbox(
            settings_frame,
            from_=1,
            to=8,
            width=5,
            textvariable=self.difficulty_var
        )
        difficulty_spinbox.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        # Mining stats frame
        stats_frame = ttk.LabelFrame(self.mining_tab, text="Mining Statistics")
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create a frame for the mining stats
        mining_stats = ttk.Frame(stats_frame)
        mining_stats.pack(fill=tk.X, pady=10)
        
        ttk.Label(mining_stats, text="Current Mining Reward:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.mining_reward_label = ttk.Label(mining_stats, text=str(MINING_REWARD))
        self.mining_reward_label.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(mining_stats, text="Blocks Mined:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.blocks_mined_label = ttk.Label(mining_stats, text="0")
        self.blocks_mined_label.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(mining_stats, text="Mining Status:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.mining_status_label = ttk.Label(mining_stats, text="Inactive")
        self.mining_status_label.grid(row=2, column=1, sticky="w", padx=5, pady=2)
        
        # Create a frame for the mining visualization
        viz_frame = ttk.LabelFrame(stats_frame, text="Mining Visualization")
        viz_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create matplotlib figure
        self.mining_figure = plt.Figure(figsize=(8, 4), dpi=100)
        self.mining_plot = self.mining_figure.add_subplot(111)
        self.mining_plot.set_title("Block Mining Time")
        self.mining_plot.set_xlabel("Block Index")
        self.mining_plot.set_ylabel("Mining Time (s)")
        
        # Create canvas for matplotlib figure
        self.mining_canvas = FigureCanvasTkAgg(self.mining_figure, viz_frame)
        self.mining_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def create_network_tab(self):
        """Create the network tab"""
        # Top frame for controls
        top_frame = ttk.Frame(self.network_tab)
        top_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(top_frame, text="Add Node", command=self.add_node_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="Remove Node", command=self.remove_node).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="Consensus", command=self.consensus).pack(side=tk.LEFT, padx=5)
        
        # Nodes frame
        nodes_frame = ttk.LabelFrame(self.network_tab, text="Connected Nodes")
        nodes_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.nodes_listbox = tk.Listbox(nodes_frame)
        self.nodes_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        nodes_scrollbar = ttk.Scrollbar(nodes_frame, orient="vertical", command=self.nodes_listbox.yview)
        self.nodes_listbox.configure(yscroll=nodes_scrollbar.set)
        nodes_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Network visualization frame
        viz_frame = ttk.LabelFrame(self.network_tab, text="Network Visualization")
        viz_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create matplotlib figure
        self.network_figure = plt.Figure(figsize=(8, 4), dpi=100)
        self.network_plot = self.network_figure.add_subplot(111)
        
        # Create canvas for matplotlib figure
        self.network_canvas = FigureCanvasTkAgg(self.network_figure, viz_frame)
        self.network_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    # ===== Core functionality methods =====
    
    def new_blockchain(self):
        """Create a new blockchain"""
        if messagebox.askyesno("New Blockchain", "Are you sure you want to create a new blockchain? All current data will be lost."):
            self.blockchain = Blockchain()
            self.refresh_blockchain()
            self.refresh_transactions()
            self.update_overview()
            self.status_label.config(text="New blockchain created")
    
    def save_data(self):
        """Save blockchain and wallet data to files"""
        try:
            # Save blockchain
            with open("blockchain.dat", "wb") as f:
                pickle.dump(self.blockchain.to_dict(), f)
                
            # Save wallets
            wallet_data = {}
            for name, wallet in self.wallets.items():
                wallet_data[name] = wallet.to_dict()
                
            with open("wallets.dat", "wb") as f:
                pickle.dump(wallet_data, f)
                
            self.status_label.config(text="Data saved successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save data: {str(e)}")
    
    def load_data(self):
        """Load blockchain and wallet data from files"""
        try:
            # Load blockchain
            if os.path.exists("blockchain.dat"):
                with open("blockchain.dat", "rb") as f:
                    blockchain_data = pickle.load(f)
                    self.blockchain = Blockchain.from_dict(blockchain_data)
                
            # Load wallets
            if os.path.exists("wallets.dat"):
                with open("wallets.dat", "rb") as f:
                    wallet_data = pickle.load(f)
                    
                    for name, data in wallet_data.items():
                        self.wallets[name] = Wallet.from_dict(data, self.blockchain)
                        
                # Update wallet combo boxes
                self.update_wallet_combos()
                
            self.refresh_blockchain()
            self.refresh_transactions()
            self.update_overview()
            self.status_label.config(text="Data loaded successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Could not load data: {str(e)}")
    
    def update_overview(self):
        """Update the overview tab with current data"""
        # Update blockchain info
        self.height_label.config(text=str(len(self.blockchain.chain)))
        self.difficulty_label.config(text=str(self.blockchain.difficulty))
        self.reward_label.config(text=str(self.blockchain.mining_reward))
        self.pending_label.config(text=str(len(self.blockchain.mempool)))
        
        # Update recent blocks
        self.blocks_tree.delete(*self.blocks_tree.get_children())
        
        for block in reversed(self.blockchain.chain[-10:]):  # Show last 10 blocks
            self.blocks_tree.insert(
                "", 
                "end", 
                values=(
                    block.index,
                    block.hash[:15] + "...",
                    len(block.transactions),
                    datetime.fromtimestamp(block.timestamp).strftime('%Y-%m-%d %H:%M:%S')
                )
            )
            
        # Update wallet info if active wallet exists
        if self.active_wallet:
            self.balance_label.config(text=str(self.active_wallet.get_balance()))
            self.address_label.config(text=self.active_wallet.public_key[:15] + "...")
            
            # Update transaction history
            self.tx_tree.delete(*self.tx_tree.get_children())
            
            history = self.active_wallet.get_transaction_history()
            for tx in sorted(history, key=lambda x: x["timestamp"], reverse=True)[:10]:  # Show last 10 transactions
                tx_type = "Sent" if tx["sender"] == self.active_wallet.public_key else "Received"
                other_address = tx["recipient"] if tx_type == "Sent" else tx["sender"]
                
                self.tx_tree.insert(
                    "",
                    "end",
                    values=(
                        tx["transaction_id"][:8] + "...",
                        tx_type,
                        other_address[:15] + "...",
                        tx["amount"],
                        datetime.fromtimestamp(tx["timestamp"]).strftime('%Y-%m-%d %H:%M:%S')
                    )
                )
    
    def refresh_blockchain(self):
        """Refresh the blockchain explorer"""
        self.blockchain_tree.delete(*self.blockchain_tree.get_children())
        
        for block in self.blockchain.chain:
            self.blockchain_tree.insert(
                "",
                "end",
                values=(
                    block.index,
                    block.hash[:15] + "...",
                    block.previous_hash[:15] + "...",
                    len(block.transactions),
                    datetime.fromtimestamp(block.timestamp).strftime('%Y-%m-%d %H:%M:%S'),
                    block.nonce
                )
            )
            
        self.update_overview()
    
    def refresh_transactions(self):
        """Refresh the transactions tab"""
        self.mempool_tree.delete(*self.mempool_tree.get_children())
        
        for tx in self.blockchain.mempool:
            self.mempool_tree.insert(
                "",
                "end",
                values=(
                    tx.transaction_id[:8] + "...",
                    tx.sender[:15] + "..." if tx.sender != "COINBASE" else "COINBASE",
                    tx.recipient[:15] + "...",
                    tx.amount,
                    tx.fee,
                    datetime.fromtimestamp(tx.timestamp).strftime('%Y-%m-%d %H:%M:%S')
                )
            )
            
        self.update_overview()
    
    def show_block_details(self, event=None):
        """Show details of the selected block"""
        # Get selected item
        if event and event.widget == self.blocks_tree:
            selection = self.blocks_tree.selection()
        elif event and event.widget == self.blockchain_tree:
            selection = self.blockchain_tree.selection()
        else:
            return
            
        if not selection:
            return
            
        item = selection[0]
        
        # Get block index
        if event.widget == self.blocks_tree:
            index = int(self.blocks_tree.item(item, "values")[0])
        else:
            index = int(self.blockchain_tree.item(item, "values")[0])
            
        # Get block
        block = self.blockchain.chain[index]
        
        # Display block details
        self.block_details_text.delete(1.0, tk.END)
        self.block_details_text.insert(tk.END, f"Block #{block.index}\n")
        self.block_details_text.insert(tk.END, f"Hash: {block.hash}\n")
        self.block_details_text.insert(tk.END, f"Previous Hash: {block.previous_hash}\n")
        self.block_details_text.insert(tk.END, f"Timestamp: {datetime.fromtimestamp(block.timestamp).strftime('%Y-%m-%d %H:%M:%S')}\n")
        self.block_details_text.insert(tk.END, f"Nonce: {block.nonce}\n")
        self.block_details_text.insert(tk.END, f"Merkle Root: {block.merkle_root}\n\n")
        self.block_details_text.insert(tk.END, f"Transactions ({len(block.transactions)}):\n")
        
        for i, tx in enumerate(block.transactions):
            self.block_details_text.insert(tk.END, f"{i+1}. {tx.transaction_id}\n")
            self.block_details_text.insert(tk.END, f"   From: {tx.sender}\n")
            self.block_details_text.insert(tk.END, f"   To: {tx.recipient}\n")
            self.block_details_text.insert(tk.END, f"   Amount: {tx.amount}\n")
            self.block_details_text.insert(tk.END, f"   Fee: {tx.fee}\n\n")
            
        # Switch to blockchain tab if needed
        if event.widget == self.blocks_tree:
            self.notebook.select(self.blockchain_tab)
    
    def show_transaction_details(self, event=None):
        """Show details of the selected transaction"""
        # Get selected item
        if event and event.widget == self.tx_tree:
            selection = self.tx_tree.selection()
        elif event and event.widget == self.mempool_tree:
            selection = self.mempool_tree.selection()
        elif event and event.widget == self.wallet_tx_tree:
            selection = self.wallet_tx_tree.selection()
        else:
            return
            
        if not selection:
            return
            
        item = selection[0]
        
        # Get transaction ID
        if event.widget == self.tx_tree:
            tx_id = self.tx_tree.item(item, "values")[0]
        elif event.widget == self.mempool_tree:
            tx_id = self.mempool_tree.item(item, "values")[0]
        else:
            tx_id = self.wallet_tx_tree.item(item, "values")[0]
            
        # Remove "..." from ID
        tx_id = tx_id.replace("...", "")
        
        # Find transaction
        tx = None
        
        # Check mempool
        for t in self.blockchain.mempool:
            if t.transaction_id.startswith(tx_id):
                tx = t
                break
                
        # Check blockchain
        if not tx:
            for block in self.blockchain.chain:
                for t in block.transactions:
                    if t.transaction_id.startswith(tx_id):
                        tx = t
                        break
                if tx:
                    break
                    
        if not tx:
            messagebox.showerror("Error", f"Transaction {tx_id} not found")
            return
            
        # Display transaction details
        self.tx_details_text.delete(1.0, tk.END)
        self.tx_details_text.insert(tk.END, f"Transaction ID: {tx.transaction_id}\n")
        self.tx_details_text.insert(tk.END, f"From: {tx.sender}\n")
        self.tx_details_text.insert(tk.END, f"To: {tx.recipient}\n")
        self.tx_details_text.insert(tk.END, f"Amount: {tx.amount}\n")
        self.tx_details_text.insert(tk.END, f"Fee: {tx.fee}\n")
        self.tx_details_text.insert(tk.END, f"Timestamp: {datetime.fromtimestamp(tx.timestamp).strftime('%Y-%m-%d %H:%M:%S')}\n")
        self.tx_details_text.insert(tk.END, f"Signature: {tx.signature}\n")
        
        # Switch to transactions tab if needed
        if event.widget == self.tx_tree or event.widget == self.wallet_tx_tree:
            self.notebook.select(self.transactions_tab)
    
    # ===== Wallet methods =====
    
    def create_wallet_dialog(self):
        """Show dialog to create a new wallet"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Create New Wallet")
        dialog.geometry("400x150")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Wallet Name:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        name_var = tk.StringVar()
        name_entry = ttk.Entry(dialog, textvariable=name_var, width=30)
        name_entry.grid(row=0, column=1, padx=10, pady=10, sticky="we")
        name_entry.focus()
        
        def create_wallet():
            name = name_var.get().strip()
            
            if not name:
                messagebox.showerror("Error", "Please enter a wallet name")
                return
                
            if name in self.wallets:
                messagebox.showerror("Error", f"Wallet '{name}' already exists")
                return
                
            # Create wallet
            wallet = Wallet(self.blockchain)
            self.wallets[name] = wallet
            
            # Update UI
            self.update_wallet_combos()
            self.wallet_var.set(name)
            self.change_wallet(None)
            
            dialog.destroy()
            self.status_label.config(text=f"Wallet '{name}' created")
            
        ttk.Button(dialog, text="Create", command=create_wallet).grid(row=1, column=0, columnspan=2, pady=20)
        
    def import_wallet_dialog(self):
        """Show dialog to import a wallet"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Import Wallet")
        dialog.geometry("500x250")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Wallet Name:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        name_var = tk.StringVar()
        name_entry = ttk.Entry(dialog, textvariable=name_var, width=30)
        name_entry.grid(row=0, column=1, padx=10, pady=10, sticky="we")
        name_entry.focus()
        
        ttk.Label(dialog, text="Private Key:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        
        private_key_var = tk.StringVar()
        private_key_entry = ttk.Entry(dialog, textvariable=private_key_var, width=50)
        private_key_entry.grid(row=1, column=1, padx=10, pady=10, sticky="we")
        
        ttk.Label(dialog, text="Public Key:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        
        public_key_var = tk.StringVar()
        public_key_entry = ttk.Entry(dialog, textvariable=public_key_var, width=50)
        public_key_entry.grid(row=2, column=1, padx=10, pady=10, sticky="we")
        
        def import_wallet():
            name = name_var.get().strip()
            private_key = private_key_var.get().strip()
            public_key = public_key_var.get().strip()
            
            if not name or not private_key or not public_key:
                messagebox.showerror("Error", "Please fill in all fields")
                return
                
            if name in self.wallets:
                messagebox.showerror("Error", f"Wallet '{name}' already exists")
                return
                
            try:
                # Create wallet
                wallet = Wallet(self.blockchain, private_key, public_key)
                self.wallets[name] = wallet
                
                # Update UI
                self.update_wallet_combos()
                self.wallet_var.set(name)
                self.change_wallet(None)
                
                dialog.destroy()
                self.status_label.config(text=f"Wallet '{name}' imported")
            except Exception as e:
                messagebox.showerror("Error", f"Could not import wallet: {str(e)}")
                
        ttk.Button(dialog, text="Import", command=import_wallet).grid(row=3, column=0, columnspan=2, pady=20)
        
    def export_wallet(self):
        """Export the active wallet"""
        if not self.active_wallet:
            messagebox.showerror("Error", "No active wallet")
            return
            
        # Get wallet name
        wallet_name = self.wallet_var.get()
        
        # Create export dialog
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Export Wallet - {wallet_name}")
        dialog.geometry("500x200")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Private Key:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        private_key_entry = ttk.Entry(dialog, width=50)
        private_key_entry.grid(row=0, column=1, padx=10, pady=10, sticky="we")
        private_key_entry.insert(0, self.active_wallet.private_key)
        
        ttk.Label(dialog, text="Public Key:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        
        public_key_entry = ttk.Entry(dialog, width=50)
        public_key_entry.grid(row=1, column=1, padx=10, pady=10, sticky="we")
        public_key_entry.insert(0, self.active_wallet.public_key)
        
        ttk.Label(dialog, text="WARNING: Never share your private key with anyone!",
                 foreground="red").grid(row=2, column=0, columnspan=2, pady=10)
                 
        ttk.Button(dialog, text="Close", command=dialog.destroy).grid(row=3, column=0, columnspan=2, pady=10)
        
    def delete_wallet(self):
        """Delete the selected wallet"""
        selection = self.wallet_listbox.curselection()
        
        if not selection:
            messagebox.showerror("Error", "No wallet selected")
            return
            
        index = selection[0]
        name = self.wallet_listbox.get(index)
        
        if messagebox.askyesno("Delete Wallet", f"Are you sure you want to delete wallet '{name}'?"):
            # Remove wallet
            del self.wallets[name]
            
            # Update UI
            self.update_wallet_combos()
            
            # Set active wallet to None if deleted
            if self.active_wallet and self.wallet_var.get() == name:
                self.active_wallet = None
                self.wallet_var.set("")
                self.update_wallet_details()
                
            self.status_label.config(text=f"Wallet '{name}' deleted")
            
    def update_wallet_combos(self):
        """Update all wallet combo boxes"""
        # Update wallet combo in overview tab
        self.wallet_combo['values'] = list(self.wallets.keys())
        
        # Update wallet listbox in wallet tab
        self.wallet_listbox.delete(0, tk.END)
        for name in self.wallets:
            self.wallet_listbox.insert(tk.END, name)
            
        # Update miner combo in mining tab
        self.miner_combo['values'] = list(self.wallets.keys())
        
    def change_wallet(self, event):
        """Change the active wallet"""
        name = self.wallet_var.get()
        
        if name in self.wallets:
            self.active_wallet = self.wallets[name]
            self.update_wallet_details()
            self.status_label.config(text=f"Switched to wallet '{name}'")
            
    def select_wallet_from_list(self, event):
        """Select a wallet from the listbox"""
        selection = self.wallet_listbox.curselection()
        
        if not selection:
            return
            
        index = selection[0]
        name = self.wallet_listbox.get(index)
        
        self.wallet_var.set(name)
        self.change_wallet(None)
        
    def update_wallet_details(self):
        """Update the wallet details in the wallet tab"""
        if not self.active_wallet:
            self.wallet_name_label.config(text="-")
            self.wallet_address_label.config(text="-")
            self.wallet_balance_label.config(text="0")
            self.wallet_tx_tree.delete(*self.wallet_tx_tree.get_children())
            return
            
        # Update wallet info
        self.wallet_name_label.config(text=self.wallet_var.get())
        self.wallet_address_label.config(text=self.active_wallet.public_key[:15] + "...")
        self.wallet_balance_label.config(text=str(self.active_wallet.get_balance()))
        
        # Update transaction history
        self.wallet_tx_tree.delete(*self.wallet_tx_tree.get_children())
        
        history = self.active_wallet.get_transaction_history()
        for tx in sorted(history, key=lambda x: x["timestamp"], reverse=True):
            tx_type = "Sent" if tx["sender"] == self.active_wallet.public_key else "Received"
            other_address = tx["recipient"] if tx_type == "Sent" else tx["sender"]
            
            if other_address == "COINBASE":
                tx_type = "Mining Reward"
                
            self.wallet_tx_tree.insert(
                "",
                "end",
                values=(
                    tx["transaction_id"][:8] + "...",
                    tx_type,
                    other_address[:15] + "...",
                    tx["amount"],
                    datetime.fromtimestamp(tx["timestamp"]).strftime('%Y-%m-%d %H:%M:%S')
                )
            )
    
    def start_mining(self):
        """Start mining new blocks"""
        if self.is_mining:
            messagebox.showinfo("Mining", "Mining is already in progress")
            return
            
        self.is_mining = True
        self.mining_thread = threading.Thread(target=self.mine_blocks)
        self.mining_thread.start()
        self.mining_status_label.config(text="Mining: Active")
    
    def stop_mining(self):
        """Stop mining new blocks"""
        self.is_mining = False
        self.mining_thread.join()
        self.mining_status_label.config(text="Mining: Inactive")
    
    def mine_blocks(self):
        """Mine new blocks in a loop"""
        while self.is_mining:
            success, block = self.blockchain.mine_pending_transactions(self.active_wallet.public_key)
            if not success:
                messagebox.showerror("Mining Error", f"Could not mine block: {block}")
                self.is_mining = False
            else:
                self.update_overview()
            time.sleep(1)  # Wait between mining attempts
    
    def toggle_auto_mining(self):
        """Toggle auto mining"""
        self.auto_mining = self.auto_mining_var.get()
    
    def show_about(self):
        """Show the about dialog"""
        messagebox.showinfo("About", "Blockchain Simulator by [Your Name]")
    
    def show_help(self):
        """Show the help dialog"""
        messagebox.showinfo("Help", "This is a blockchain simulator. Use it to explore and interact with the blockchain.")
    
    def validate_blockchain(self):
        """Validate the entire blockchain"""
        if self.blockchain.is_chain_valid():
            messagebox.showinfo("Blockchain Validation", "The blockchain is valid")
        else:
            messagebox.showerror("Blockchain Validation", "The blockchain is invalid")
    
    def export_blockchain(self):
        """Export the blockchain to a file"""
        # Implement the export functionality
        pass
    
    def create_transaction_dialog(self):
        """Show dialog to create a new transaction"""
        # Implement the create transaction functionality
        pass
    
    def add_node_dialog(self):
        """Show dialog to add a new node"""
        # Implement the add node functionality
        pass
    
    def remove_node(self):
        """Remove the selected node"""
        # Implement the remove node functionality
        pass
    
    def consensus(self):
        """Implement the consensus functionality"""
        # Implement the consensus functionality
        pass
    
    def send_transaction(self):
        """Send a transaction from the active wallet"""
        if not self.active_wallet:
            messagebox.showerror("Error", "No active wallet")
            return
            
        recipient = self.recipient_entry.get().strip()
        amount_str = self.amount_entry.get().strip()
        fee_str = self.fee_entry.get().strip()
        
        if not recipient or not amount_str or not fee_str:
            messagebox.showerror("Error", "Please fill in all fields")
            return
            
        try:
            amount = float(amount_str)
            fee = float(fee_str)
        except ValueError:
            messagebox.showerror("Error", "Amount and fee must be numbers")
            return
            
        try:
            success, result = self.active_wallet.send(recipient, amount, fee)
            
            if success:
                messagebox.showinfo("Transaction", f"Transaction sent with ID: {result}")
                self.recipient_entry.delete(0, tk.END)
                self.amount_entry.delete(0, tk.END)
                self.fee_entry.delete(0, tk.END)
                self.fee_entry.insert(0, "1")
                self.refresh_transactions()
                self.update_wallet_details()
            else:
                messagebox.showerror("Error", f"Could not send transaction: {result}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not send transaction: {str(e)}")

# Main entry point
if __name__ == "__main__":
    root = tk.Tk()
    app = BlockchainGUI(root)
    root.mainloop() 