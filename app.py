print("app.py has been imported") #this is just to check if the file is being imported for debugging purposes
from flask import Flask, flash, render_template, url_for, redirect, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, logout_user, current_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
import email_validator
import os
from dotenv import load_dotenv
import base64
import json
from datetime import datetime
from datetime import datetime, timedelta
from sqlalchemy import event
from sqlalchemy.sql import func
from helper import * 
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()

app = Flask(__name__, 
    static_folder='static', 
    template_folder='templates'  # Ensure this is set correctly
)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
db = SQLAlchemy(app)
bcrypt =Bcrypt(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(150), nullable=False)
    last_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(150), nullable=False)

class Package(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipient_name = db.Column(db.String(200), nullable=False)
    sender_name = db.Column(db.String(200), nullable=True)
    recipient_address = db.Column(db.String(300), nullable=True)
    extra_details = db.Column(db.Text, nullable=True)
    image_path = db.Column(db.String(300), nullable=True)
    date_received = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_picked_up = db.Column(db.Boolean, default=False)
    picked_up_date = db.Column(db.DateTime, nullable=True)

class Student(db.Model):
    student_id = db.Column(db.String(10), primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)

class SignupForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    submit = SubmitField('Sign Up')

    #checks if the email already exists in the database
    def validate_email(self, email):
        existing_user = User.query.filter_by(email=email.data).first()
        if existing_user:
            raise ValidationError('That email already exists. Login instead.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


# not sure if we might have an home page, this will reroute there if we do
# @app.route('/')
# def index():
#         return render_template('index.html')

@app.route('/')
def index():
    form = LoginForm()
    return render_template('index.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():            
        if not form.email.data.endswith('@my.fisk.edu'):
            flash('Please use your Fisk email to login', 'danger')
        else:
            user = User.query.filter_by(email=form.email.data).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('scan'))
            else:
                flash('Login unsuccessful. Please check email and password', 'danger')            
                return redirect(url_for('index'))
        
    return render_template('index.html', form=form)

@app.route('/scan')
@login_required
def scan():
    return render_template('scan.html')

@app.route('/orders')
@login_required
def orders():
    # Fetch all packages ordered by date (newest first)
    packages = Package.query.order_by(Package.date_received.desc()).all()
    
    # Calculate latest pickup date for each package (3 days after date received)
    for package in packages:
        package.latest_pickup_date = package.date_received + timedelta(days=3)
    
    # Calculate counts for each category
    total_count = len(packages)
    current_count = sum(1 for package in packages if not package.is_picked_up)
    picked_up_count = sum(1 for package in packages if package.is_picked_up)
    
    # Calculate overdue packages (packages not picked up and older than 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    overdue_count = sum(1 for package in packages if not package.is_picked_up and package.date_received < seven_days_ago)
    
    return render_template('orders.html', 
                          packages=packages, 
                          total_count=total_count,
                          current_count=current_count,
                          picked_up_count=picked_up_count,
                          overdue_count=overdue_count)

@app.route('/confirm')
@login_required
def confirm():
    # Get the image path from session if available
    image_path = session.get('temp_image_path', None)
    
    # Initialize label as None
    label = None
    
    # Check if we have temp package details from previous edits
    temp_details = session.get('temp_package_details', None)
    
    # Only try to generate label details if an image path exists and we don't have temp details
    if image_path and not temp_details:
        try:
            label = generate_label_details()
            print("Generated new label details from Mindee API")
        except Exception as e:
            flash(f"Error processing package details: {str(e)}", "danger")
            print(f"Error processing package details: {str(e)}")
    elif temp_details:
        # Use temp details to reconstruct the label
        label = Label(
            recipient_name=temp_details.get('recipient_name', ''),
            recipient_address=temp_details.get('recipient_address', ''),
            sender_name=temp_details.get('sender_name', '')
        )
        print(f"Using saved form values: Recipient={temp_details.get('recipient_name')}, Sender={temp_details.get('sender_name')}")
    
    return render_template('confirm.html', image_path=image_path, label=label)

def send_email(to_email, subject, message):
    try:
        # Get email credentials from environment variables
        email_username = os.environ.get('EMAIL_USERNAME')
        email_password = os.environ.get('EMAIL_PASSWORD')
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = email_username
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Add message body
        msg.attach(MIMEText(message, 'plain'))
        
        # Connect to Gmail SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        
        # Login and send email
        server.login(email_username, email_password)
        server.send_message(msg)
        server.quit()
        
        print(f"Email sent successfully to {to_email}")
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

@app.route('/save_package', methods=['POST'])
@login_required
def save_package():
    try:
        # Get form data
        recipient_name = request.form.get('recipientName')
        sender_name = request.form.get('senderName')
        recipient_address = request.form.get('recipientAddress')
        extra_details = request.form.get('extraDetails')
        
        # Get image path from session
        image_path = session.get('temp_image_path')
        
        # Create new package record
        new_package = Package(
            recipient_name=recipient_name,
            sender_name=sender_name,
            recipient_address=recipient_address,
            extra_details=extra_details,
            image_path=image_path
        )
        
        # Save to database
        db.session.add(new_package)
        db.session.commit()
        
        # Try to match student in different ways
        student = None
        
        # Method 1: Exact match by full name
        student = Student.query.filter_by(full_name=recipient_name).first()
        
        # Method 2: Case-insensitive match if method 1 failed
        if not student:
            student = Student.query.filter(
                func.lower(Student.full_name) == func.lower(recipient_name)
            ).first()
        
        # Method 3: Check if recipient name contains the student's name
        if not student:
            # Get all students
            all_students = Student.query.all()
            # Check if any student name is contained within the recipient name
            for s in all_students:
                if s.full_name.lower() in recipient_name.lower() or recipient_name.lower() in s.full_name.lower():
                    student = s
                    break
        
        if student:
            # Send email notification to the student
            subject = "Package Notification from Fisk University Mailroom"
            message = f"""
Hello {student.full_name},

You have a package waiting for you at the Fisk University Mailroom.

Package Details:
- Sender: {sender_name}
- Date Received: {datetime.now().strftime('%Y-%m-%d %H:%M')}
- You have 3 days to pick up your package

Please bring your student ID to pick up your package.

Best regards,
Fisk University Mailroom
"""
            
            # Send the email notification
            email_sent = send_email(student.email, subject, message)
            if email_sent:
                flash(f'Success! Package uploaded to orders and email notification sent to {student.email}', 'success')
            else:
                flash(f'Package uploaded to orders but email notification failed to send to {student.email}. Please check email settings.', 'warning')
        else:
            flash('Package uploaded to orders. No matching student found in the database, so no email notification was sent.', 'info')
        
        # Clear the session variables
        session.pop('temp_image_path', None)
        session.pop('temp_package_details', None)
        
        return redirect(url_for('orders'))
        
    except Exception as e:
        flash(f'Error saving package information: {str(e)}', 'danger')
        return redirect(url_for('confirm'))

@app.route('/process_image', methods=['POST'])
@login_required
def process_image():
    try:
        data = request.json
        image_data = data.get('imageData')
        
        # Remove the data URL prefix
        if image_data and ',' in image_data:
            image_data = image_data.split(',')[1]
        else:
            return jsonify({
                'success': False,
                'message': "Invalid image data format"
            }), 400
        
        # Create directories if they don't exist
        upload_dir = os.path.join('static', 'uploads')
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        
        # Generate a unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = "package.jpg"
        filepath = os.path.join(upload_dir, filename)
        
        # Save the image to filesystem
        with open(filepath, "wb") as f:
            f.write(base64.b64decode(image_data))
        
        # Store the image path in session for the confirmation step
        session['temp_image_path'] = os.path.join('uploads', filename)
        
        return jsonify({
            'success': True,
            'message': 'Image processed successfully',
            'image_path': os.path.join('uploads', filename)
        })
    
    except Exception as e:
        print(f"Error processing image: {e}")
        return jsonify({
            'success': False,
            'message': f"Error processing image: {str(e)}"
        }), 500

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        if not form.email.data.endswith('@my.fisk.edu'):
            flash('Please use your Fisk email to sign up', 'danger')
        else:
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User(first_name=form.first_name.data, last_name=form.last_name.data, email=form.email.data, password=hashed_password)
            db.session.add(user)
            db.session.commit()
            flash('Account created successfully! You can now log in.', 'success')
            return redirect(url_for('index'))
    return render_template('signup.html', form=form)

@app.route('/mark_picked_up/<int:package_id>', methods=['POST'])
@login_required
def mark_picked_up(package_id):
    try:
        # Get the package
        package = Package.query.get_or_404(package_id)
        
        # Set pickup status and time
        package.is_picked_up = True
        package.picked_up_date = datetime.utcnow()
        db.session.commit()
        
        # Try to find matching student for email notification
        student = None
        recipient_name = package.recipient_name
        
        # Method 1: Exact match by full name
        student = Student.query.filter_by(full_name=recipient_name).first()
        
        # Method 2: Case-insensitive match if method 1 failed
        if not student:
            student = Student.query.filter(
                func.lower(Student.full_name) == func.lower(recipient_name)
            ).first()
        
        # Method 3: Check if recipient name contains the student's name
        if not student:
            # Get all students
            all_students = Student.query.all()
            # Check if any student name is contained within the recipient name
            for s in all_students:
                if s.full_name.lower() in recipient_name.lower() or recipient_name.lower() in s.full_name.lower():
                    student = s
                    break
        
        # Send email notification if student found
        email_sent = False
        if student:
            # Create pickup confirmation email
            subject = "Package Pickup Confirmation - Fisk University Mailroom"
            message = f"""
Hello {student.full_name},

This email confirms that you have successfully picked up your package from the Fisk University Mailroom.

Package Details:
- Sender: {package.sender_name}
- Date Received: {package.date_received.strftime('%Y-%m-%d %H:%M')}
- Date Picked Up: {package.picked_up_date.strftime('%Y-%m-%d %H:%M')}

Thank you for using the Fisk University Mailroom services.

Best regards,
Fisk University Mailroom
"""
            # Send the email notification
            email_sent = send_email(student.email, subject, message)
            print(f"Pickup confirmation email sent to {student.email}: {email_sent}")
        
        # Return success with email status
        return jsonify({
            'success': True,
            'email_sent': email_sent,
            'student_email': student.email if student else None
        })
        
    except Exception as e:
        print(f"Error marking package as picked up: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/update_package_details', methods=['POST'])
@login_required
def update_package_details():
    try:
        # Get updated package details from the request
        data = request.json
        
        # Store in session for persistence between page navigations
        session['temp_package_details'] = {
            'recipient_name': data.get('recipientName', ''),
            'sender_name': data.get('senderName', ''),
            'recipient_address': data.get('recipientAddress', '')
        }
        
        # Print statement to show update is working
        print(f"Package details updated: Recipient={data.get('recipientName')}, Sender={data.get('senderName')}, Address={data.get('recipientAddress')}")
        
        return jsonify({
            'success': True,
            'message': 'Package details updated successfully'
        })
        
    except Exception as e:
        print(f"Error updating package details: {e}")
        return jsonify({
            'success': False,
            'message': f"Error updating package details: {str(e)}"
        }), 500

@app.route('/get_package_counts')
@login_required
def get_package_counts():
    # Fetch all packages
    packages = Package.query.all()
    
    # Calculate counts for each category
    total_count = len(packages)
    current_count = sum(1 for package in packages if not package.is_picked_up)
    picked_up_count = sum(1 for package in packages if package.is_picked_up)
    
    # Calculate overdue packages (packages not picked up and older than 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    overdue_count = sum(1 for package in packages if not package.is_picked_up and package.date_received < seven_days_ago)
    
    return jsonify({
        'total_count': total_count,
        'current_count': current_count,
        'picked_up_count': picked_up_count,
        'overdue_count': overdue_count
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
