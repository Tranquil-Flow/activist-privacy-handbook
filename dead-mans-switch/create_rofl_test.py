#!/usr/bin/env python3
import subprocess
import time
import json
import sys
import requests
import os
import logging

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rofl_test_debug.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

API_BASE_URL = "http://localhost:5000/api"

def run_curl_command(cmd):
    """Run a curl command and return the result"""
    logger.debug(f"Executing curl: {cmd}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            logger.info("✅ Command executed successfully:")
            logger.debug(f"Command output: {result.stdout}")
            return result.stdout
        else:
            logger.error("❌ Command failed:")
            logger.error(f"Error output: {result.stderr}")
            return None
    except Exception as e:
        logger.error(f"❌ Error executing command: {e}")
        return None

def check_rofl_service():
    """Check ROFL service status and return detailed information"""
    logger.info("Checking ROFL service status...")
    
    # Check if process is running
    result = subprocess.run("ps aux | grep -i 'app.py\\|start_rofl.py' | grep -v grep", 
                           shell=True, capture_output=True, text=True)
    
    if result.stdout.strip():
        logger.info("✅ ROFL service process found:")
        logger.debug(f"Process details:\n{result.stdout}")
        
        # Check if the service is responding to API calls
        try:
            response = requests.get(f"{API_BASE_URL}/health")
            if response.status_code == 200:
                logger.info("✅ ROFL API is responding")
                logger.debug(f"Health check response: {response.text}")
            else:
                logger.warning(f"⚠️ ROFL API returned status {response.status_code}")
        except requests.exceptions.ConnectionError:
            logger.error("❌ ROFL API is not responding")
            return False
        
        # Check ROFL logs for recent activity
        if os.path.exists("rofl_debug.log"):
            logger.info("Checking recent ROFL logs...")
            log_check = subprocess.run("tail -n 50 rofl_debug.log", 
                                     shell=True, capture_output=True, text=True)
            logger.debug(f"Recent ROFL logs:\n{log_check.stdout}")
        
        return True
    else:
        logger.error("❌ ROFL service process not found!")
        return False

def create_alert_for_rofl():
    """Create a new alert via curl with short check-in time for ROFL to catch"""
    logger.info("Creating alert with short check-in time...")
    
    # Create an alert with a 15-second check-in window
    cmd = """curl -X POST http://localhost:5000/api/alerts -H "Content-Type: application/json" -d '{"user_id": "0x70997970C51812dc3A010C7d01b50e0d17dc79C8", "message": "ROFL TEST ALERT - This should be auto-triggered by ROFL", "group_id": "-1002687819162", "expiry_seconds": 3600, "check_in_seconds": 15}'"""
    response = run_curl_command(cmd)
    
    if response:
        try:
            data = json.loads(response)
            alert_id = data.get("alert_id")
            if alert_id:
                logger.info(f"📝 Alert created successfully with ID: {alert_id}")
                logger.debug(f"Full alert response: {response}")
                return alert_id
        except json.JSONDecodeError as e:
            logger.error(f"⚠️ Failed to parse response JSON: {e}")
            logger.debug(f"Raw response: {response}")
    return None

def check_alert_status(alert_id, max_attempts=6, wait_seconds=15):
    """Try to check if the alert still exists or was triggered by ROFL with retries"""
    logger.info(f"Starting alert status check for alert_id: {alert_id}")
    
    for attempt in range(max_attempts):
        logger.info(f"\nAttempt {attempt+1}/{max_attempts} to check if alert was triggered...")
        
        # Check ROFL service status
        if not check_rofl_service():
            logger.error("ROFL service is not running properly. Attempting to restart...")
            subprocess.Popen(["python3", "start_rofl.py"], 
                           start_new_session=True, 
                           stdout=open("rofl_debug.log", "a"), 
                           stderr=subprocess.STDOUT)
            logger.info("Waiting 5 seconds for ROFL service to initialize...")
            time.sleep(5)
        
        # Check alert status
        url = f"{API_BASE_URL}/alerts/{alert_id}"
        logger.info(f"Checking alert status at: {url}")
        
        try:
            response = requests.get(url)
            logger.debug(f"Status code: {response.status_code}")
            logger.debug(f"Response: {response.text}")
            
            if response.status_code == 404 or "Alert not found" in response.text:
                logger.info("✅ Alert not found - checking if it was triggered by ROFL...")
                
                # Check ROFL logs for trigger confirmation
                if os.path.exists("rofl_debug.log"):
                    logger.info("Checking ROFL logs for trigger confirmation...")
                    trigger_check = subprocess.run(
                        f"grep -A 5 'TRIGGER_ALERT_BY_ROFL' rofl_debug.log | tail -n 20",
                        shell=True, capture_output=True, text=True
                    )
                    logger.debug(f"Trigger logs:\n{trigger_check.stdout}")
                    
                    # Check for Telegram message sending
                    telegram_check = subprocess.run(
                        f"grep -A 5 'telegram.Bot' rofl_debug.log | tail -n 20",
                        shell=True, capture_output=True, text=True
                    )
                    logger.debug(f"Telegram logs:\n{telegram_check.stdout}")
                
                return True
            else:
                logger.info(f"⏳ Alert still exists. Waiting {wait_seconds} seconds...")
                
                # On last attempt, try to force a ROFL scan
                if attempt == max_attempts - 1:
                    logger.warning("⚠️ Last attempt - triggering ROFL scan...")
                    trigger_cmd = f"curl -X POST {API_BASE_URL}/scan"
                    run_curl_command(trigger_cmd)
                    time.sleep(wait_seconds + 10)
                else:
                    time.sleep(wait_seconds)
        
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error checking alert status: {e}")
            time.sleep(wait_seconds)
    
    logger.error("❌ Alert was not triggered within the time window")
    return False

def main():
    logger.info("Starting ROFL test script...")
    
    # Initial ROFL service check
    if not check_rofl_service():
        logger.info("Starting ROFL service...")
        subprocess.Popen(["python3", "start_rofl.py"], 
                       start_new_session=True, 
                       stdout=open("rofl_debug.log", "a"), 
                       stderr=subprocess.STDOUT)
        logger.info("Waiting 5 seconds for ROFL service to initialize...")
        time.sleep(5)
    
    # Create test alert
    alert_id = create_alert_for_rofl()
    if not alert_id:
        logger.error("Cannot proceed without alert ID")
        sys.exit(1)
    
    logger.info("\n⏱️ Waiting 30 seconds for ROFL to process the alert...")
    time.sleep(30)
    
    # Check alert status with detailed logging
    success = check_alert_status(alert_id, max_attempts=6, wait_seconds=15)
    
    if success:
        logger.info("✅ Test completed: Alert was triggered")
    else:
        logger.error("❌ Test failed: Alert was not triggered")
        logger.info("Check rofl_debug.log and rofl_test_debug.log for detailed information")

if __name__ == "__main__":
    main() 