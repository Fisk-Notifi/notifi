from app import app, db, Student

# Specific student data
students_data = [
    ('T001', 'Ifeoluwa Shode', 'ijshode09@my.fisk.edu'),
    ('T002', 'Folusho Adeyemi', 'fvadeyemi05@my.fisk.edu'),
    ('T003', 'Frank Inyiama', 'fuinyiama09@my.fisk.edu'),
    ('T004', 'Emmanuel Adeyemi', 'eiadeyemi05@my.fisk.edu')
]

def create_students():
    with app.app_context():
        # Clear existing data
        Student.query.delete()
        
        # Create students from the provided data
        for student_id, full_name, email in students_data:
            student = Student(
                student_id=student_id,
                full_name=full_name,
                email=email
            )
            db.session.add(student)
        
        # Commit the changes
        db.session.commit()
        print("Successfully added the following students to the database:")
        for student_id, full_name, email in students_data:
            print(f"ID: {student_id}, Name: {full_name}, Email: {email}")

if __name__ == '__main__':
    create_students() 