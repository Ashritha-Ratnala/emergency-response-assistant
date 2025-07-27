#!/usr/bin/env python3
"""
Emergency Response Assistant - Application Entry Point
"""

import os
import sys
from backend.app import app
from config import config

def create_app():
    """Create and configure the Flask application"""
    
    # Get configuration from environment
    config_name = os.getenv('FLASK_CONFIG', 'default')
    app.config.from_object(config[config_name])
    
    return app

if __name__ == '__main__':
    # Create application
    application = create_app()
    
    # Get host and port from environment
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    
    print(f"""
    🚨 Emergency Response Assistant
    ================================
    🌐 Server: http://{host}:{port}
    🔧 Environment: {os.getenv('FLASK_CONFIG', 'default')}
    📱 Ready to process emergencies!
    ================================
    """)
    
    # Run application
    application.run(
        host=host,
        port=port,
        debug=application.config.get('DEBUG', False)
    )