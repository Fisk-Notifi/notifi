from app import app, db, Package, Student, send_email
from datetime import datetime
import os

def add_test_package():
    with app.app_context():
        # Find the test student
        student = Student.query.filter_by(student_id="12345").first()
        
        if not student:
            print("Test student not found. Please run add_test_student.py first.")
            return
            
        # Create a test package
        new_package = Package(
            recipient_name=student.full_name,
            sender_name="Test Sender",
            recipient_address="123 Test Street",
            extra_details="This is a test package",
            image_path=None,
            date_received=datetime.utcnow()
        )
        
        # Save to database
        db.session.add(new_package)
        db.session.commit()
        
        print(f"Test package added for {student.full_name}")
        
        # Send email notification
        subject = "Package Notification from Fisk University Mailroom"
        message = f"""
Hello {student.full_name},

You have a package waiting for you at the Fisk University Mailroom.

Package Details:
- Sender: {new_package.sender_name}
- Date Received: {new_package.date_received.strftime('%Y-%m-%d %H:%M')}
- You have 3 days to pick up your package

Please bring your student ID to pick up your package.

Best regards,
Fisk University Mailroom
"""
        
        # Send the email notification
        email_sent = send_email(student.email, subject, message)
        if email_sent:
            print(f"Email notification sent to {student.email}")
        else:
            print(f"Failed to send email notification to {student.email}")

if __name__ == "__main__":
    add_test_package() 