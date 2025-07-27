import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'emergency-response-secret-key-2024')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Email configuration
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    EMAIL_USER = os.getenv('EMAIL_USER', 'your-email@gmail.com')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', 'your-app-password')
    
    # Emergency contacts (in production, use a database)
    EMERGENCY_CONTACTS = [
        {
            "name": "Emergency Services",
            "phone": "911",
            "email": os.getenv('EMERGENCY_EMAIL', 'emergency@local.gov')
        },
        {
            "name": "Primary Contact",
            "phone": os.getenv('PRIMARY_PHONE', '+1234567890'),
            "email": os.getenv('PRIMARY_EMAIL', 'primary@example.com')
        },
        {
            "name": "Secondary Contact", 
            "phone": os.getenv('SECONDARY_PHONE', '+0987654321'),
            "email": os.getenv('SECONDARY_EMAIL', 'secondary@example.com')
        }
    ]
    
    # Classification settings
    URGENCY_THRESHOLD = int(os.getenv('URGENCY_THRESHOLD', '7'))  # Minimum urgency to send alerts
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    
class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}