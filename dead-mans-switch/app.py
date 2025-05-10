import os
import json
import time
from datetime import datetime, timedelta
from telegram import Bot
from cryptography.fernet import Fernet
import logging
import asyncio

# ---
# NOTE: For MVP/demo/testing only! The Telegram bot token is hardcoded below.
# For production, replace this with an environment variable or secure secret management.
TELEGRAM_TOKEN = "8082498715:AAG7Gz33_f5qVLj-egFPlCmEgShfFqX5p4s"
# ---

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DeadManSwitch:
    def __init__(self):
        # Generate encryption key for this session
        self.key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.key)
        
        # Use the hardcoded Telegram token for MVP/demo
        self.telegram_token = TELEGRAM_TOKEN
        self.bot = Bot(token=self.telegram_token) if self.telegram_token else None
        
        # In-memory config (ephemeral)
        self.config = {
            'alerts': {},
            'check_interval': 86400,  # Default: 24 hours
            'last_check_in': None
        }

    def _save_config(self):
        # No-op: config is only in memory for this session
        pass

    def _load_config(self):
        # No-op: config is only in memory for this session
        pass

    def create_alert(self, alert_id, message, group_id, expiry_days, check_in_days):
        """Create a new alert configuration"""
        self.config['alerts'][alert_id] = {
            'message': message,
            'group_id': group_id,
            'expiry_date': (datetime.now() + timedelta(days=expiry_days)).isoformat(),
            'check_in_days': check_in_days,
            'created_at': datetime.now().isoformat(),
            'last_check_in': datetime.now().isoformat()
        }
        return alert_id

    def check_in(self, alert_id):
        """Update the last check-in time for an alert"""
        if alert_id in self.config['alerts']:
            self.config['alerts'][alert_id]['last_check_in'] = datetime.now().isoformat()
            return True
        return False

    def trigger_alert(self, alert_id):
        """Manually trigger an alert"""
        if alert_id not in self.config['alerts']:
            return False
        
        alert = self.config['alerts'][alert_id]
        if self.bot:
            try:
                async def send():
                    await self.bot.send_message(
                        chat_id=alert['group_id'],
                        text=f"🚨 ALERT TRIGGERED 🚨\n\n{alert['message']}"
                    )
                asyncio.run(send())
                return True
            except Exception as e:
                logger.error(f"Error sending alert: {e}")
        return False

    def check_alerts(self):
        """Check all alerts and trigger if conditions are met"""
        current_time = datetime.now()
        expired_alerts = []
        for alert_id, alert in self.config['alerts'].items():
            # Check if alert has expired
            expiry_date = datetime.fromisoformat(alert['expiry_date'])
            if current_time > expiry_date:
                expired_alerts.append(alert_id)
                continue
            # Check if check-in period has passed
            last_check_in = datetime.fromisoformat(alert['last_check_in'])
            check_in_deadline = last_check_in + timedelta(days=alert['check_in_days'])
            if current_time > check_in_deadline:
                self.trigger_alert(alert_id)
                expired_alerts.append(alert_id)
        # Remove expired/triggered alerts
        for alert_id in expired_alerts:
            del self.config['alerts'][alert_id]

def main():
    switch = DeadManSwitch()
    while True:
        switch.check_alerts()
        time.sleep(switch.config['check_interval'])

if __name__ == "__main__":
    main() 