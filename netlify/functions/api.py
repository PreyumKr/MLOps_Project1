# netlify/functions/api.py
"""
Netlify serverless function for FastAPI application.
Wraps the FastAPI app with Mangum ASGI adapter for AWS Lambda runtime.
"""
from mangum import Mangum
import sys
import os

# Add parent directories to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from main import app  # Import the 'app' instance from main.py

# Netlify looks for a 'handler' export for serverless functions
handler = Mangum(app)