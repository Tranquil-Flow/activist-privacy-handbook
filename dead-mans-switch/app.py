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
            contract_address = os.getenv('CONTRACT_ADDRESS')  # Deployed contract address
            if not contract_address:
                raise ValueError("CONTRACT_ADDRESS environment variable not set")
            self.contract_address = Web3.to_checksum_address(contract_address)
        
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

    def create_alert(self, user_id: str, message: str, group_id: str, expiry_seconds: int, check_in_seconds: int) -> str:
        """Create a new alert."""
        alert_id = Web3.keccak(text=f"{user_id}{message}{group_id}{int(time.time())}").hex()
        alert_id_bytes = Web3.to_bytes(hexstr=alert_id)
        logger.info(f"[CREATE_ALERT] alert_id_bytes (hex): {alert_id_bytes.hex()}")
        tx = self.contract.functions.createAlert(
            alert_id_bytes,
            message,
            group_id,
            expiry_seconds,
            check_in_seconds
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
            logger.info(f"[TRIGGER_ALERT] alert_id_bytes (hex): {alert_id_bytes.hex()}")
            
            # Fetch alert details BEFORE triggering (since triggering deletes the alert)
            alert = self.contract.functions.alerts(alert_id_bytes).call()
            logger.info(f"Fetched alert before triggering: {alert}")
            
            # Check if alert exists
            if alert[0] == '0x0000000000000000000000000000000000000000':
                return "Alert does not exist or has already been triggered"
                
            # Save alert details we'll need after it's deleted
            group_id = alert[2]  # groupId
            message = alert[1]   # message
            
            # Now trigger the alert (which will delete it from the contract)
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
                
            # Send Telegram message with the details we saved BEFORE triggering
            telegram_success = True
            if self.bot:
                import asyncio
                try:
                    loop = asyncio.get_running_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(self.bot.send_message(chat_id=group_id, text=f"🚨 MANUAL ALERT TRIGGERED 🚨\n\n{message}"))
                except Exception as e:
                    # Don't fail the entire operation if Telegram fails
                    logger.error(f"Error sending Telegram message: {e}")
                    telegram_success = False
            
            if not telegram_success:
                logger.warning("Alert was triggered in contract, but Telegram notification failed")
                
            return True
        except Exception as e:
            logger.error(f"Error triggering alert: {e}")
            return str(e)

    def trigger_alert_by_rofl(self, alert_id: str):
        """Trigger an alert automatically by ROFL (dead man's switch) and return True on success, or the error message on failure."""
        try:
            alert_id_bytes = Web3.to_bytes(hexstr=alert_id)
            logger.info(f"[TRIGGER_ALERT_BY_ROFL] alert_id_bytes (hex): {alert_id_bytes.hex()}")
            
            # Fetch alert details BEFORE triggering (since triggering deletes the alert)
            alert = self.contract.functions.alerts(alert_id_bytes).call()
            logger.info(f"Fetched alert before ROFL triggering: {alert}")
            
            # Check if alert exists
            if alert[0] == '0x0000000000000000000000000000000000000000':
                return "Alert does not exist or has already been triggered"
                
            # Save alert details we'll need after it's deleted
            group_id = alert[2]  # groupId
            message = alert[1]   # message
            
            # Now trigger the alert (which will delete it from the contract)
            tx = self.contract.functions.triggerAlertByROFL(alert_id_bytes).build_transaction({
                'from': self.admin_account.address,
                'gas': 2000000,
                'gasPrice': self.web3.eth.gas_price,
                'nonce': self.web3.eth.get_transaction_count(self.admin_account.address),
            })
            signed_tx = self.admin_account.sign_transaction(tx)
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status != 1:
                logger.error("ROFL trigger transaction reverted.")
                return "Transaction reverted"
                
            # Send Telegram message with the details we saved BEFORE triggering
            telegram_success = True
            if self.bot:
                import asyncio
                try:
                    loop = asyncio.get_running_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(self.bot.send_message(chat_id=group_id, text=f"🚨 DEAD MANS SWITCH TRIGGERED 🚨\n\n{message}"))
                except Exception as e:
                    # Don't fail the entire operation if Telegram fails
                    logger.error(f"Error sending Telegram message: {e}")
                    telegram_success = False
            
            if not telegram_success:
                logger.warning("Alert was triggered in contract, but Telegram notification failed")
                
            return True
        except Exception as e:
            logger.error(f"Error triggering alert by ROFL: {e}")
            return str(e)

    def check_alerts(self, alert_id: str):
        """Fetch and log all stored info for a given alert from the contract."""
        alert_id_bytes = Web3.to_bytes(hexstr=alert_id)
        alert = self.contract.functions.alerts(alert_id_bytes).call()
        logger.info(f"Fetched alert from contract: {alert}")
        return alert

    def scan_alerts_for_rofl(self, run_once=False):
        """
        Scan for alerts that need to be triggered by ROFL due to missed check-ins.
        If run_once is False, this will run in an infinite loop, checking periodically.
        If run_once is True, it will do a single scan and return.
        """
        check_interval = 10  # seconds between checks
        
        def perform_scan():
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logger.info(f"[{timestamp}] 🔍 SCAN STARTED: Checking for alerts that need to be triggered...")
            current_time = int(time.time())
            
            try:
                # Get recent events for alert creation
                # Limit to 100 blocks to avoid RPC limits
                block_number = self.web3.eth.block_number
                from_block = max(0, block_number - 100)  # Last 100 blocks to avoid RPC limits
                
                # Get alert creation events
                alert_events = self.contract.events.AlertCreated.get_logs(from_block=from_block)
                
                logger.info(f"Found {len(alert_events)} recent alert events to check")
                alerts_triggered = 0
                
                for event in alert_events:
                    alert_id_bytes = event.args.alertId
                    alert_id_hex = alert_id_bytes.hex()
                    
                    # Get alert details
                    alert = self.contract.functions.alerts(alert_id_bytes).call()
                    
                    # Check if alert exists (user address is not zero)
                    if alert[0] == '0x0000000000000000000000000000000000000000':
                        continue
                    
                    # Parse alert details
                    user_address = alert[0]
                    expiry_time = alert[3]    # expiryTime 
                    check_in_seconds = alert[4]  # checkInSeconds
                    last_check_in = alert[6]  # lastCheckIn
                    
                    logger.info(f"Checking alert {alert_id_hex}:")
                    logger.info(f"  User: {user_address}")
                    logger.info(f"  Last check-in: {last_check_in}")
                    logger.info(f"  Check-in seconds: {check_in_seconds}")
                    logger.info(f"  Expiry time: {expiry_time}")
                    logger.info(f"  Current time: {current_time}")
                    
                    # Check conditions for triggering:
                    # 1. Check-in deadline missed (current_time > last_check_in + check_in_seconds)
                    # 2. Not expired (current_time < expiry_time)
                    deadline_missed = current_time > (last_check_in + check_in_seconds)
                    not_expired = current_time < expiry_time
                    
                    if deadline_missed and not_expired:
                        logger.info(f"⚠️ Alert {alert_id_hex} has missed check-in deadline. Triggering...")
                        result = self.trigger_alert_by_rofl(alert_id_hex)
                        
                        if result is True:
                            logger.info(f"✅ Alert {alert_id_hex} triggered successfully by ROFL")
                            alerts_triggered += 1
                        else:
                            logger.error(f"❌ Failed to trigger alert {alert_id_hex}: {result}")
                
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                logger.info(f"[{timestamp}] ✓ SCAN COMPLETE: {'No alerts needed triggering' if alerts_triggered == 0 else f'Triggered {alerts_triggered} alerts'}. Next scan in {check_interval} seconds.")
                return alerts_triggered
                
            except Exception as e:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                logger.error(f"[{timestamp}] ❌ SCAN ERROR: {e}")
                return 0
        
        if run_once:
            return perform_scan()
        
        # Continuous monitoring loop
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"[{timestamp}] 🚀 Starting continuous ROFL monitoring (checking every {check_interval} seconds)...")
        while True:
            perform_scan()
            time.sleep(check_interval)

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
    # Create the DeadManSwitch instance
    switch = DeadManSwitch()
    
    # Start monitoring for alerts that need to be triggered by ROFL
    logger.info("Starting Dead Man's Switch ROFL monitoring service")
    switch.scan_alerts_for_rofl(run_once=False)  # This runs in an infinite loop

if __name__ == "__main__":
    main() 