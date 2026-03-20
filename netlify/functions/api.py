# netlify/functions/api.py
from mangum import Mangum
from app import app # Import the 'app' instance from your app.py file

handler = Mangum(app)