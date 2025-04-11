import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Print all environment variables
print("All environment variables:")
for key, value in os.environ.items():
    # Don't print passwords directly
    if 'PASSWORD' in key or 'SECRET' in key:
        masked_value = '*' * 8
        print(f"{key}: {masked_value}")
    else:
        print(f"{key}: {value}")

# Specifically check our email variables
print("\nEmail Configuration:")
email_username = os.environ.get('EMAIL_USERNAME')
email_password = os.environ.get('EMAIL_PASSWORD') 
print(f"EMAIL_USERNAME: {email_username}")
print(f"EMAIL_PASSWORD: {'*' * len(email_password) if email_password else 'Not set'}") 