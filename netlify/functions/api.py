# netlify/functions/api.py
from mangum import Mangum
from main import app # Import the 'app' instance from your app.py file

handler = Mangum(app)