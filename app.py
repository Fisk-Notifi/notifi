print("app.py has been imported") #this is just to check if the file is being imported for debugging purposes
from flask import Flask, flash, render_template, url_for, redirect
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
from datetime import datetime, timedelta
from sqlalchemy import event
from sqlalchemy.sql import func

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

class Order(db.Model):
    order_id = db.Column(db.String(10), primary_key=True)
    student_name = db.Column(db.String(150), nullable=False)
    sender_info = db.Column(db.String(150), nullable=False)
    student_email = db.Column(db.String(150), nullable=False)
    late_pickup_date = db.Column(db.String(150), nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now())

    def __init__(self, **kwargs):
        super(Order, self).__init__(**kwargs)
        if not self.order_id:
            # Get the last order
            last_order = Order.query.order_by(Order.order_id.desc()).first()
            
            if last_order:
                # Extract the number from the last order_id and increment it
                last_num = int(last_order.order_id.split('-')[1])
                new_num = last_num + 1
            else:
                # If no orders exist, start with 1
                new_num = 1
            
            # Format the new order_id with leading zeros
            self.order_id = f"ORD-{new_num:03d}"
            
        # Set late_pickup_date to current date + 3 days
        if not self.late_pickup_date:
            self.late_pickup_date = (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')

@event.listens_for(Order, 'before_insert')
def set_order_id(mapper, connection, target):
    if not target.order_id:
        # Get the last order
        last_order = Order.query.order_by(Order.order_id.desc()).first()
        
        if last_order:
            # Extract the number from the last order_id and increment it
            last_num = int(last_order.order_id.split('-')[1])
            new_num = last_num + 1
        else:
            # If no orders exist, start with 1
            new_num = 1
            
        # Format the new order_id with leading zeros
        target.order_id = f"ORD-{new_num:03d}"
        
    # Set late_pickup_date to current date + 3 days
    if not target.late_pickup_date:
        target.late_pickup_date = (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')

class Student(db.Model):
    student_id = db.Column(db.String(10), primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)

class Package(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipient_name = db.Column(db.String(200))
    sender_name = db.Column(db.String(200))
    recipient_address = db.Column(db.String(300))
    extra_details = db.Column(db.Text)
    image_path = db.Column(db.String(300))
    date_received = db.Column(db.DateTime)
    is_picked_up = db.Column(db.Boolean)
    picked_up_date = db.Column(db.DateTime)

    def __init__(self, **kwargs):
        super(Package, self).__init__(**kwargs)
        if not self.date_received:
            self.date_received = datetime.now()
        if not self.is_picked_up:
            self.is_picked_up = False

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
    return render_template('orders.html')

@app.route('/confirm')
@login_required
def confirm():
    return render_template('confirm.html')

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
 

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
