#!/usr/bin/env python3
import requests
import time
import json
import sys
import subprocess

API_BASE_URL = "http://localhost:5000/api"

def create_alert(user_id, message, group_id, expiry_seconds, check_in_seconds):
    """Create a new alert via API"""
    url = f"{API_BASE_URL}/alerts"
    payload = {
        "user_id": user_id,
        "message": message,
        "group_id": group_id,
        "expiry_seconds": expiry_seconds,
        "check_in_seconds": check_in_seconds
    }
    
    print(f"Creating alert with payload: {payload}")
    response = requests.post(url, json=payload)
    
    if response.status_code == 201:
        data = response.json()
        print(f"✅ Alert created successfully: {data['alert_id']}")
        return data['alert_id']
    else:
        print(f"❌ Failed to create alert: {response.text}")
        return None

def check_in(user_id, alert_id):
    """Check in on an alert via API"""
    url = f"{API_BASE_URL}/alerts/{alert_id}/check-in"
    payload = {"user_id": user_id}
    
    print(f"Checking in on alert: {alert_id}")
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        print("✅ Check-in successful")
        return True
    else:
        print(f"❌ Check-in failed: {response.text}")
        return False

def trigger_alert(user_id, alert_id):
    """Manually trigger an alert via API using the curl command known to work"""
    print(f"Triggering alert: {alert_id}")
    
    # The exact curl command that's known to work
    curl_command = f"curl -X POST http://localhost:5000/api/alerts/{alert_id}/trigger -H \"Content-Type: application/json\" -d '{{\"user_id\": \"{user_id}\"}}'"
    
    print(f"DEBUG: Executing command: {curl_command}")
    
    # Execute the curl command
    try:
        result = subprocess.run(
            curl_command,
            shell=True,
            capture_output=True,
            text=True
        )
        
        print(f"DEBUG: Curl command return code: {result.returncode}")
        print(f"DEBUG: Curl stdout: {result.stdout}")
        
        if result.returncode == 0:
            try:
                response = json.loads(result.stdout)
                print(f"✅ Alert triggered successfully")
                return True
            except json.JSONDecodeError:
                print(f"✅ Command executed but response was not JSON: {result.stdout}")
                return True
        else:
            print(f"❌ Command failed with error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error executing command: {e}")
        return False

def main():
    # User wallet address - use your test address
    user_id = "0xD73D744BB1295f21b03886f3c8EAde60A7eC1756"
    
    # Telegram group ID
    group_id = "2687819162"
    
    # Create an alert that will expire in 1 hour with a check-in requirement of 5 minutes
    alert_id = create_alert(
        user_id=user_id,
        message="Test alert created via API",
        group_id=group_id,
        expiry_seconds=3600,  # 1 hour
        check_in_seconds=300  # 5 minutes
    )
    
    if not alert_id:
        print("Cannot proceed without alert ID")
        sys.exit(1)
    
    # Check in on the alert
    check_in(user_id, alert_id)
    
    # Trigger the alert
    trigger_alert(user_id, alert_id)

if __name__ == "__main__":
    main() 