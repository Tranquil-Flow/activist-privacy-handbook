from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
from app import DeadManSwitch
import logging
import secrets

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize the dead man's switch
switch = DeadManSwitch()

@app.route('/api/alerts', methods=['POST'])
def create_alert():
    """Create a new alert"""
    data = request.get_json()
    required_fields = ['user_id', 'message', 'group_id', 'expiry_days', 'check_in_days']
    
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        alert_id = switch.create_alert(
            user_id=data['user_id'],
            message=data['message'],
            group_id=data['group_id'],
            expiry_days=int(data['expiry_days']),
            check_in_days=int(data['check_in_days'])
        )
        
        if alert_id:
            return jsonify({
                'alert_id': alert_id,
                'message': 'Alert created successfully'
            }), 201
        else:
            return jsonify({'error': 'Failed to create alert'}), 500
            
    except Exception as e:
        logger.error(f"Error creating alert: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/alerts/<alert_id>/check-in', methods=['POST'])
def check_in(alert_id):
    """Update the last check-in time for an alert"""
    data = request.get_json()
    if 'user_id' not in data:
        return jsonify({'error': 'Missing user_id'}), 400
        
    try:
        success = switch.check_in(user_id=data['user_id'], alert_id=alert_id)
        if success:
            return jsonify({'message': 'Check-in successful'}), 200
        else:
            return jsonify({'error': 'Alert not found or failed to check in'}), 404
    except Exception as e:
        logger.error(f"Error during check-in: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/alerts/<alert_id>/trigger', methods=['POST'])
def trigger_alert(alert_id):
    """Manually trigger an alert"""
    data = request.get_json()
    if 'user_id' not in data:
        return jsonify({'error': 'Missing user_id'}), 400
        
    try:
        result = switch.trigger_alert(user_id=data['user_id'], alert_id=alert_id)
        if result is True:
            return jsonify({'message': 'Alert triggered successfully'}), 200
        else:
            return jsonify({'error': f'Alert not found or failed to trigger: {result}'}), 404
    except Exception as e:
        logger.error(f"Error triggering alert: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/alerts', methods=['GET'])
def list_alerts():
    """List all active alerts (not implemented)"""
    return jsonify({'error': 'Listing alerts is not implemented in contract-backed mode.'}), 501

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 