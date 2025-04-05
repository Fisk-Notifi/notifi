print("app.py has been imported")
from flask import Flask, flash, render_template, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
# from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, LoginManager, login_user, logout_user, current_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
import email_validator
import os


app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notifi.db'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://postgres:notifidatabase123@localhost/notifi')
app.config['SECRET_KEY'] = 'your_secret_key'
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

class SignupForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    submit = SubmitField('Sign Up')

    #checks is the email already exists in the database
# In your validate_email method
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
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('successfullogintest'))
        else:
            flash('Login unsuccessful. Please check email and password', 'danger')
    return render_template('index.html', form=form)

@app.route('/successfullogintest', methods=['GET', 'POST'])
@login_required
def successfullogintest():
    return render_template('successfullogintest.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
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
