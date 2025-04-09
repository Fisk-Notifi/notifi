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
    return render_template('orders.html', packages=packages)

@app.route('/confirm')
@login_required
def confirm():
    # Get the image path from session if available
    image_path = session.get('temp_image_path', None)
    
    # Initialize label as None
    label = None
    
    # Only try to generate label details if an image path exists
    if image_path:
        try:
            label = generate_label_details()
        except Exception as e:
            flash(f"Error processing package details: {str(e)}", "danger")
            print(f"Error processing package details: {str(e)}")
    
    return render_template('confirm.html', image_path=image_path, label=label)

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
        
        # Clear the session variable
        session.pop('temp_image_path', None)
        
        flash('Package information saved successfully!', 'success')
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
        package = Package.query.get_or_404(package_id)
        package.is_picked_up = True
        package.picked_up_date = datetime.utcnow()
        db.session.commit()
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
