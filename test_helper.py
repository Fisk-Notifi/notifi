import os
from dotenv import load_dotenv
from helper import generate_label_details

# Load environment variables
load_dotenv()

# Debug information
print(f"MINDEE_API_KEY: {os.environ.get('MINDEE_API_KEY', 'Not set')}")

# Try to use the function from helper.py
result = generate_label_details()
if result:
    print("Label details successfully generated:")
    print(f"Recipient Name: {result.recipient_name}")
    print(f"Recipient Address: {result.recipient_address}")
else:
    print("Failed to generate label details") 