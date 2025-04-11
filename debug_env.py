import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Print all environment variables for debugging
print("Environment variables loaded:")
print(f"MINDEE_API_KEY: {os.environ.get('MINDEE_API_KEY', 'Not set')}")
print(f"DATABASE_URL: {os.environ.get('DATABASE_URL', 'Not set')}")
print(f"SECRET_KEY: {os.environ.get('SECRET_KEY', 'Not set')}") 