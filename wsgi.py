import sys
import os

# Add the project folder to the Python path
path = '/home/YOUR_USERNAME/smart-financier'
if path not in sys.path:
    sys.path.insert(0, path)

# Set environment variables
os.environ['FLASK_ENV'] = 'production'
os.environ['SECRET_KEY'] = 'change-this-to-a-long-random-secret-key'

from app import create_app
application = create_app()
