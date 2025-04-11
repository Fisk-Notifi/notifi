from dotenv import load_dotenv, dotenv_values
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def test_email():
    # Load env variables directly from file
    env_vars = dotenv_values(".env")
    email_username = env_vars.get('EMAIL_USERNAME')
    email_password = env_vars.get('EMAIL_PASSWORD')
    
    print(f"Reading directly from .env file:")
    print(f"Email username: {email_username}")
    print(f"Email password: {'*' * len(email_password)}")  # Don't print actual password
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = email_username
    msg['To'] = email_username  # Send to self for testing
    msg['Subject'] = "Test Email from Notifi App"
    
    # Add message body
    message = "This is a test email to verify if the email sending functionality works."
    msg.attach(MIMEText(message, 'plain'))
    
    try:
        # Connect to Gmail SMTP server
        print("Connecting to SMTP server...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        
        # Login and send email
        print(f"Logging in with username: {email_username}")
        server.login(email_username, email_password)
        
        print("Sending email...")
        server.send_message(msg)
        server.quit()
        
        print("Email sent successfully!")
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

if __name__ == "__main__":
    test_email() 