# netlify/functions/api.py
"""
Netlify serverless function for FastAPI application.
"""
import sys
import os

# Add root directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from mangum import Mangum
from main import app

# Handler for Netlify Functions
handler = Mangum(app)