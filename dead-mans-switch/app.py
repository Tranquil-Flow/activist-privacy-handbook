import os
import json
import time
from datetime import datetime, timedelta
from telegram import Bot
import logging
import asyncio
import base64
from web3 import Web3
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class DeadManSwitch:
    def __init__(self):
        # Get the Telegram token from ROFL secrets
        self.telegram_token = os.getenv('TELEGRAM_TOKEN')
        self.bot = Bot(token=self.telegram_token) if self.telegram_token else None
        
        # Initialize Web3 connection to Sapphire Testnet
        self.web3 = Web3(Web3.HTTPProvider(os.getenv('SAPPHIRE_RPC_URL', 'https://testnet.sapphire.oasis.dev')))
        
        # Load admin private key from environment variable
        private_key = os.getenv('PRIVATE_KEY')
        if not private_key:
            raise ValueError("PRIVATE_KEY environment variable not set")
        self.admin_account = self.web3.eth.account.from_key(private_key)
        print(f"[DEBUG] Admin address: {self.admin_account.address}")
        
        # Load the contract ABI and address
        with open('contracts/DeadManSwitch.json', 'r') as f:
            contract_data = json.load(f)
            self.contract_abi = contract_data['abi']
            self.contract_address = os.getenv('CONTRACT_ADDRESS')  # Deployed contract address
        
        self.contract = self.web3.eth.contract(address=self.contract_address, abi=self.contract_abi)
        
        # Default check interval
        self.check_interval = 86400  # 24 hours

    def _sign_and_send_transaction(self, transaction):
        """Helper method to sign and send a transaction using the admin account"""
        transaction['nonce'] = self.web3.eth.get_transaction_count(self.admin_account.address)
        gas_price = self.web3.eth.gas_price
        transaction['maxFeePerGas'] = gas_price
        transaction['maxPriorityFeePerGas'] = gas_price
        transaction['type'] = 2  # EIP-1559
        transaction['chainId'] = 23295  # Sapphire Testnet chain ID
        if 'gasPrice' in transaction:
            del transaction['gasPrice']
        signed_tx = self.admin_account.sign_transaction(transaction)
        tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        return self.web3.eth.wait_for_transaction_receipt(tx_hash)

    def create_alert(self, user_id: str, message: str, group_id: str, expiry_days: int, check_in_days: int) -> str:
        """Create a new alert."""
        alert_id = Web3.keccak(text=f"{user_id}{message}{group_id}{int(time.time())}").hex()
        alert_id_bytes = Web3.to_bytes(hexstr=alert_id)
        
        tx = self.contract.functions.createAlert(
            alert_id_bytes,
            message,
            group_id,
            expiry_days,
            check_in_days
        ).build_transaction({
            'from': self.admin_account.address,
            'gas': 2000000,
            'gasPrice': self.web3.eth.gas_price,
            'nonce': self.web3.eth.get_transaction_count(self.admin_account.address),
        })
        
        signed_tx = self.admin_account.sign_transaction(tx)
        tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        self.web3.eth.wait_for_transaction_receipt(tx_hash)
        
        return alert_id

    def check_in(self, user_id: str, alert_id: str) -> bool:
        """Check in on an alert."""
        try:
            alert_id_bytes = Web3.to_bytes(hexstr=alert_id)
            tx = self.contract.functions.checkIn(alert_id_bytes).build_transaction({
                'from': self.admin_account.address,
                'gas': 2000000,
                'gasPrice': self.web3.eth.gas_price,
                'nonce': self.web3.eth.get_transaction_count(self.admin_account.address),
            })
            
            signed_tx = self.admin_account.sign_transaction(tx)
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            self.web3.eth.wait_for_transaction_receipt(tx_hash)
            return True
        except Exception as e:
            logger.error(f"Error checking in: {str(e)}")
            return False

    def trigger_alert(self, user_id: str, alert_id: str):
        """Trigger an alert and return True on success, or the error message on failure."""
        try:
            alert_id_bytes = Web3.to_bytes(hexstr=alert_id)
            tx = self.contract.functions.triggerAlertByAdmin(alert_id_bytes).build_transaction({
                'from': self.admin_account.address,
                'gas': 2000000,
                'gasPrice': self.web3.eth.gas_price,
                'nonce': self.web3.eth.get_transaction_count(self.admin_account.address),
            })
            signed_tx = self.admin_account.sign_transaction(tx)
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            if receipt.status != 1:
                logger.error("Trigger transaction reverted.")
                return "Transaction reverted"
            return True
        except Exception as e:
            logger.error(f"Error triggering alert: {e}")
            return str(e)

    def check_alerts(self):
        """Check all users' alerts and trigger if conditions are met."""
        # This method is no longer needed as the smart contract handles alert triggering
        pass
    

    # TODO: Fix this
    def set_rofl_app_id(self, rofl_app_id: str) -> bool:
        """Set the ROFL App ID (admin only)."""
        try:
            tx = self.contract.functions.setRoflAppID(rofl_app_id).build_transaction({
                'from': self.admin_account.address,
                'gas': 2000000,
                'gasPrice': self.web3.eth.gas_price,
                'nonce': self.web3.eth.get_transaction_count(self.admin_account.address),
            })
            signed_tx = self.admin_account.sign_transaction(tx)
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            return receipt.status == 1
        except Exception as e:
            logger.error(f"Error setting ROFL App ID: {e}")
            print(f"Error setting ROFL App ID: {e}")
            return False

def main():
    switch = DeadManSwitch()
    while True:
        switch.check_alerts()
        time.sleep(switch.check_interval)

if __name__ == "__main__":
    main() 