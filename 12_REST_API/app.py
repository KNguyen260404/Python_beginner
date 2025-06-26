#!/usr/bin/env python3
"""
REST API Application Entry Point
"""

import os
from app import create_app

# Create Flask application instance
app = create_app(os.getenv('FLASK_ENV', 'development'))

if __name__ == '__main__':
    # Run the application
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 