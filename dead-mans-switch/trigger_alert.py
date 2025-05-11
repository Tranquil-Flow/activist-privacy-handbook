#!/usr/bin/env python3
import subprocess
import sys
import json

def trigger_alert_with_curl(alert_id, user_id):
    """
    Trigger an alert using the exact curl command that's known to work
    """
    print(f"Triggering alert {alert_id} for user {user_id} using curl...")
    
    # The exact curl command that's known to work
    curl_command = [
        "curl", "-X", "POST", 
        f"http://localhost:5000/api/alerts/{alert_id}/trigger",
        "-H", "Content-Type: application/json",
        "-d", f'{{"user_id": "{user_id}"}}'
    ]
    
    # Execute the curl command
    try:
        result = subprocess.run(
            curl_command,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            try:
                response = json.loads(result.stdout)
                print(f"✅ Alert triggered successfully: {response}")
            except json.JSONDecodeError:
                print(f"✅ Command executed but response was not JSON: {result.stdout}")
        else:
            print(f"❌ Command failed with error: {result.stderr}")
    except Exception as e:
        print(f"❌ Error executing command: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python trigger_alert.py <alert_id> <user_id>")
        print("Example: python trigger_alert.py 28563983c38a5c9d3372785531c2084f58d4ba41eda309f4128fe6dbf766dc49 0x70997970C51812dc3A010C7d01b50e0d17dc79C8")
        sys.exit(1)
    
    alert_id = sys.argv[1]
    user_id = sys.argv[2]
    
    trigger_alert_with_curl(alert_id, user_id) 