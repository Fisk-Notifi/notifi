from app import app, db, Student
from dotenv import dotenv_values

def update_student_email():
    # Get email from .env file
    env_vars = dotenv_values(".env")
    email = env_vars.get('EMAIL_USERNAME')
    
    with app.app_context():
        # Find the test student
        student = Student.query.filter_by(student_id="12345").first()
        
        if student:
            old_email = student.email
            student.email = email
            db.session.commit()
            print(f"Updated student email from {old_email} to {email}")
        else:
            print("Test student not found")

if __name__ == "__main__":
    update_student_email() 