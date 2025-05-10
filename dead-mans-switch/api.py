from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
from app import DeadManSwitch
import logging

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
    try:
        data = request.json
        required_fields = ['message', 'group_id', 'expiry_days', 'check_in_days']
        
        # Validate required fields
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Generate a unique ID for the alert
        alert_id = str(uuid.uuid4())
        
        # Create the alert
        switch.create_alert(
            alert_id=alert_id,
            message=data['message'],
            group_id=data['group_id'],
            expiry_days=data['expiry_days'],
            check_in_days=data['check_in_days']
        )
        
        return jsonify({
            'alert_id': alert_id,
            'message': 'Alert created successfully'
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating alert: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/alerts/<alert_id>/check-in', methods=['POST'])
def check_in(alert_id):
    """Update the last check-in time for an alert"""
    try:
        success = switch.check_in(alert_id)
        if success:
            return jsonify({'message': 'Check-in successful'}), 200
        return jsonify({'error': 'Alert not found'}), 404
    except Exception as e:
        logger.error(f"Error during check-in: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/alerts/<alert_id>/trigger', methods=['POST'])
def trigger_alert(alert_id):
    """Manually trigger an alert"""
    try:
        success = switch.trigger_alert(alert_id)
        if success:
            return jsonify({'message': 'Alert triggered successfully'}), 200
        return jsonify({'error': 'Alert not found or failed to trigger'}), 404
    except Exception as e:
        logger.error(f"Error triggering alert: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/alerts', methods=['GET'])
def list_alerts():
    """List all active alerts"""
    try:
        # Return only non-sensitive information
        alerts = {
            alert_id: {
                'expiry_date': alert['expiry_date'],
                'check_in_days': alert['check_in_days'],
                'created_at': alert['created_at'],
                'last_check_in': alert['last_check_in']
            }
            for alert_id, alert in switch.config['alerts'].items()
        }
        return jsonify(alerts), 200
    except Exception as e:
        logger.error(f"Error listing alerts: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 