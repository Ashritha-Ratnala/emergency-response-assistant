from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import json
from datetime import datetime
from classifier import EmergencyClassifier
from email_alert import EmailAlert
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__,static_folder='../static',
            template_folder='templates')
CORS(app)

# Initialize components
classifier = EmergencyClassifier()
email_alert = EmailAlert()

# Emergency contacts (in production, this would be in a database)
EMERGENCY_CONTACTS = [
    {"name": "Emergency Services", "phone": "911", "email": "emergency@local.gov"},
    {"name": "Primary Contact", "phone": "+1234567890", "email": "primary@example.com"},
    {"name": "Secondary Contact", "phone": "+0987654321", "email": "secondary@example.com"}
]

@app.route('/')
def index():
    """Render the main interface"""
    return render_template('index.html')

@app.route('/api/process-emergency', methods=['POST'])
def process_emergency():
    """Process emergency voice input and trigger alerts"""
    try:
        data = request.get_json()
        
        # Extract data
        transcript = data.get('transcript', '').strip()
        location = data.get('location', {})
        timestamp = datetime.now().isoformat()
        
        if not transcript:
            return jsonify({"error": "No transcript provided"}), 400
        
        # Classify emergency
        classification = classifier.classify_emergency(transcript)
        
        # Prepare emergency data
        emergency_data = {
            "timestamp": timestamp,
            "transcript": transcript,
            "location": location,
            "classification": classification,
            "contacts_notified": []
        }
        
        # Send alerts based on urgency
        if classification['urgency'] >= 7:  # High urgency
            alert_result = email_alert.send_emergency_alert(emergency_data, EMERGENCY_CONTACTS)
            emergency_data['contacts_notified'] = alert_result.get('notified', [])
        
        # Log emergency
        logger.info(f"Emergency processed: {classification['type']} - Urgency: {classification['urgency']}")
        
        return jsonify({
            "success": True,
            "emergency_data": emergency_data,
            "message": f"Emergency classified as {classification['type']} with urgency level {classification['urgency']}"
        })
        
    except Exception as e:
        logger.error(f"Error processing emergency: {str(e)}")
        return jsonify({"error": "Failed to process emergency"}), 500

@app.route('/api/test-alert', methods=['POST'])
def test_alert():
    """Test the alert system"""
    try:
        test_data = {
            "timestamp": datetime.now().isoformat(),
            "transcript": "This is a test emergency alert",
            "location": {"latitude": 40.7128, "longitude": -74.0060},
            "classification": {"type": "Test", "urgency": 5, "keywords": ["test"]}
        }
        
        result = email_alert.send_emergency_alert(test_data, EMERGENCY_CONTACTS[:1])  # Send to first contact only
        
        return jsonify({
            "success": True,
            "message": "Test alert sent successfully",
            "result": result
        })
        
    except Exception as e:
        logger.error(f"Error sending test alert: {str(e)}")
        return jsonify({"error": "Failed to send test alert"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)