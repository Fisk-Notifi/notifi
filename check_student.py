from app import app, db, Student

with app.app_context():
    student = Student.query.filter_by(student_id="12345").first()
    if student:
        print(f"Student found: {student.full_name}, {student.email}")
    else:
        print("No student found") 