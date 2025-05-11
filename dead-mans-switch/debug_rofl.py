#!/usr/bin/env python3
import sys
import os
from app import DeadManSwitch
import logging
import time

# Configure logging to file
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("rofl_debug.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Start the ROFL monitoring service with enhanced debugging"""
    print("🚀 Starting Dead Man's Switch ROFL monitoring service with DEBUG logging")
    try:
        # Create the DeadManSwitch instance
        switch = DeadManSwitch()
        
        # Log contract address
        logger.info(f"CONTRACT ADDRESS: {switch.contract_address}")
        logger.info(f"ADMIN ADDRESS: {switch.admin_account.address}")
        
        # Run a single scan first to check functionality
        logger.info("Running a single test scan...")
        alerts_triggered = switch.scan_alerts_for_rofl(run_once=True)
        logger.info(f"Test scan complete, alerts triggered: {alerts_triggered}")
        
        # Start monitoring for alerts that need to be triggered by ROFL
        print("✅ ROFL service initialized, starting continuous monitoring")
        logger.info("Starting continuous monitoring...")
        switch.scan_alerts_for_rofl(run_once=False)  # This runs in an infinite loop
    except Exception as e:
        logger.error(f"Failed to start ROFL service: {e}", exc_info=True)
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Print diagnostic information
    logger.info(f"Current working directory: {os.getcwd()}")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Starting in {os.path.abspath(__file__)}")
    
    main() 