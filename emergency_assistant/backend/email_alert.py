import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class EmailAlert:
    def __init__(self):
        """Initialize email alert system"""
        # Email configuration
        self.smtp_server = 'smtp.gmail.com'
        self.smtp_port = 587
        self.email_user = 'aasritharatnala05@gmail.com'
        self.email_password = 'ysjbqkbsxggsjtep'  # App password from Gmail

    def send_emergency_alert(self, emergency_data: dict, contacts: list) -> dict:
        """Send emergency alert to all contacts if urgency > 7"""
        results = {'notified': [], 'failed': []}

        urgency_level = emergency_data['classification']['urgency']
        if urgency_level <= 7:
            logger.info("Urgency level is not high enough to trigger alerts.")
            return results

        for contact in contacts:
            try:
                if contact.get('email'):
                    success = self._send_email(emergency_data, contact)
                    if success:
                        results['notified'].append(contact['name'])
                    else:
                        results['failed'].append(contact['name'])

            except Exception as e:
                logger.error(f"Failed to notify {contact['name']}: {str(e)}")
                results['failed'].append(contact['name'])

        return results

    def _send_email(self, emergency_data: dict, contact: dict) -> bool:
        """Send email alert to a specific contact"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_user
            msg['To'] = contact['email']
            msg['Subject'] = f"🚨 EMERGENCY ALERT - {emergency_data['classification']['type'].upper()}"

            # Create email body
            body = self._create_email_body(emergency_data, contact)
            msg.attach(MIMEText(body, 'html'))

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_password)
                server.send_message(msg)

            logger.info(f"Emergency alert sent to {contact['name']} ({contact['email']})")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {contact['email']}: {str(e)}")
            return False

    def _create_email_body(self, emergency_data: dict, contact: dict) -> str:
        """Create HTML email body"""
        classification = emergency_data['classification']
        location = emergency_data.get('location', {})

        # Format location
        if location.get('latitude') and location.get('longitude'):
            location_text = f"GPS: {location['latitude']:.6f}, {location['longitude']:.6f}"
            maps_link = f"https://maps.google.com/?q={location['latitude']},{location['longitude']}"
        else:
            location_text = classification.get('location_mentioned', 'Location not available')
            maps_link = None

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .alert-header {{ background-color: #ff4444; color: white; padding: 20px; border-radius: 5px; }}
                .emergency-details {{ background-color: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                .urgency-high {{ color: #ff0000; font-weight: bold; }}
                .urgency-medium {{ color: #ff8800; font-weight: bold; }}
                .urgency-low {{ color: #008800; font-weight: bold; }}
                .map-link {{ display: inline-block; background-color: #007bff; color: white; padding: 10px 15px; text-decoration: none; border-radius: 3px; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="alert-header">
                <h1>🚨 EMERGENCY ALERT</h1>
                <p>Dear {contact['name']}, an emergency has been reported and requires immediate attention.</p>
            </div>

            <div class="emergency-details">
                <h2>Emergency Details</h2>
                <p><strong>Time:</strong> {emergency_data['timestamp']}</p>
                <p><strong>Type:</strong> {classification['type'].replace('_', ' ').title()}</p>
                <p><strong>Urgency Level:</strong>
                    <span class="{'urgency-high' if classification['urgency'] >= 8 else 'urgency-medium' if classification['urgency'] >= 5 else 'urgency-low'}">
                        {classification['urgency']}/10
                    </span>
                </p>
                <p><strong>Location:</strong> {location_text}</p>
                <p><strong>Description:</strong> "{emergency_data['transcript']}"</p>

                {f'<a href="{maps_link}" class="map-link" target="_blank">📍 View on Google Maps</a>' if maps_link else ''}
            </div>

            <div class="emergency-details">
                <h3>What to do:</h3>
                <ul>
                    <li>If this is a life-threatening emergency, call 911 immediately</li>
                    <li>Contact the person who reported this emergency if possible</li>
                    <li>Consider dispatching emergency services if you are authorized</li>
                    <li>Document any actions taken</li>
                </ul>
            </div>

            <p><small>This alert was generated automatically by the Emergency Response Assistant system.</small></p>
        </body>
        </html>
        """

        return html_body
