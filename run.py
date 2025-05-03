# At the top of run.py
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from dotenv import load_dotenv


load_dotenv()
# Load environment variables from .env file

# # Add project root to Python path
# sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


# Create an instance of the Flask application
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
