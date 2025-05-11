#!/usr/bin/env python3
import time
import sys
import logging
from app import DeadManSwitch

# Configure logging to reduce the debug noise
logging.getLogger('web3').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('asyncio').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('httpcore').setLevel(logging.WARNING)

def test_all_functionality():
    # Initialize the dead man's switch
    print("🚀 Initializing DeadManSwitch...")
    switch = DeadManSwitch()
    
    # Step 1: Create a new alert
    print("\n📝 STEP 1: Creating a new alert...")
    user_id = switch.admin_account.address
    message = "This is a test alert created for testing purposes."
    group_id = "-2687819162"  # Telegram group IDs should be negative for groups
    expiry_seconds = 3600  # 1 hour
    check_in_seconds = 300  # 5 minutes
    
    try:
        alert_id = switch.create_alert(
            user_id=user_id,
            message=message,
            group_id=group_id,
            expiry_seconds=expiry_seconds,
            check_in_seconds=check_in_seconds
        )
        print(f"✅ Successfully created alert: {alert_id}")
    except Exception as e:
        print(f"❌ Failed to create alert: {e}")
        return
    
    # Step 2: Check alert details from the contract
    print("\n🔍 STEP 2: Checking alert details from contract...")
    try:
        alert_details = switch.check_alerts(alert_id)
        print(f"📊 Alert details: {alert_details}")
    except Exception as e:
        print(f"❌ Failed to check alert details: {e}")
    
    # Step 3: Check in on the alert
    print("\n✋ STEP 3: Checking in on the alert...")
    try:
        success = switch.check_in(user_id=user_id, alert_id=alert_id)
        if success:
            print("✅ Successfully checked in on alert")
        else:
            print("❌ Failed to check in on alert")
    except Exception as e:
        print(f"❌ Error checking in: {e}")
    
    # Step 4: Try triggering the alert manually (as admin)
    print("\n🚨 STEP 4: Triggering alert manually...")
    try:
        result = switch.trigger_alert(user_id=user_id, alert_id=alert_id)
        if result is True:
            print("✅ Successfully triggered alert manually")
        else:
            print(f"❌ Failed to trigger alert: {result}")
    except Exception as e:
        print(f"❌ Error triggering alert: {e}")
    
    print("\n✨ Testing complete!")

if __name__ == "__main__":
    test_all_functionality() 