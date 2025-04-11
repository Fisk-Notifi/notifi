from app import app, db, Student

def add_test_student():
    with app.app_context():
        # Check if the student already exists
        existing_student = Student.query.filter_by(student_id="12345").first()
        if existing_student:
            print(f"Test student already exists: {existing_student.full_name}, {existing_student.email}")
            return
            
        # Create a test student
        test_student = Student(
            student_id="12345",
            full_name="John Doe",
            email="testnotifiapp@gmail.com"  # Using the email from .env for testing
        )
        
        # Add to database
        db.session.add(test_student)
        db.session.commit()
        print(f"Test student added: {test_student.full_name}, {test_student.email}")

if __name__ == "__main__":
    add_test_student() 