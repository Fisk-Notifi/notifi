# Notifi App

A Flask-based application for managing package notifications and QR code scanning for students. This application streamlines the package delivery notification process in educational institutions.

## Features
- User authentication (signup/login) with Fisk email addresses
- QR code scanning functionality for package tracking
- Package management system with status tracking
- Automated email notifications when packages arrive
- Student package tracking dashboard
- Database migrations support
- Secure password hashing
- Form validation and CSRF protection
- Admin panel for package management

## Prerequisites
- Python 3.x
- pip (Python package manager)
- Git
- Mindee API (for scanning feature)
- PostgreSQL (for production) or SQLite (for development)
- SMTP server for email notifications

## Setup and Installation

1. Clone the repository:
```bash
git clone https://github.com/Fisk-Notifi/notifi.git
cd Notifi
```

2. Create a virtual environment and activate it:
```bash
# On macOS/Linux
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
.\venv\Scripts\activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with the following variables:
```
DATABASE_URL=”postgresql://….”
SECRET_KEY=”your_secret_key_here”
MINDEE_API_KEY=”your_mindee_api_key”
EMAIL_USERNAME=your_email_username
EMAIL_PASSWORD=your_app_password
```

Here's how to obtain these values:
- `DATABASE_URL`: For local development, you can use the SQLite path shown above. For production, set up a PostgreSQL database and use its connection string.
- `SECRET_KEY`: Generate a strong random string for securing sessions and tokens. You can use Python to generate one: `python -c "import secrets; print(secrets.token_hex(16))"`.
- `MINDEE_API_KEY`: Sign up at [Mindee](https://platform.mindee.com/) and create an API key in your account dashboard.
- `EMAIL_USERNAME`: Your Gmail address (e.g., example@gmail.com) for sending notifications.
- `EMAIL_PASSWORD`: Use an app password, not your regular Gmail password. Follow [Google's instructions](https://support.google.com/accounts/answer/185833) to create one.


5. Initialize the database:
```bash
flask db init
flask db migrate
flask db upgrade
```

6. Run the application:
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Usage

### Admin Users
- Login with admin credentials to access the admin dashboard
- Scan QR codes on packages using the integrated scanner
- Add package information manually if needed
- Mark packages as delivered or picked up
- View package history and status

### Student Users
- Register with a valid school email address
- Receive email notifications when packages arrive
- View package status and history on the dashboard
- Get notified when packages have been delivered or picked up

## Dependencies
- Flask (3.0.0) - Web framework
- Flask-SQLAlchemy (3.1.1) - Database ORM
- Flask-Login (0.6.3) - User authentication
- Flask-WTF (1.2.1) - Form handling
- WTForms (3.1.1) - Form validation
- email-validator (2.1.0.post1) - Email validation
- Flask-Bcrypt (1.0.1) - Password hashing
- Flask-Migrate (4.0.5) - Database migrations
- python-dotenv (1.0.0) - Environment variable management
- psycopg2-binary (2.9.10) - PostgreSQL adapter
- mindee (4.20.0) - QR code scanning

## Project Structure
```
notifi/
├── app.py                   # Main application file
├── helper.py                # Helper functions
├── templates/               # HTML templates
├── static/                  # Static files (CSS, JS, images)
├── migrations/              # Database migrations
├── instance/                # Instance-specific files
│   └── database.db          # SQLite database (development)
├── requirements.txt         # Project dependencies
├── .env                     # Environment variables
├── check_db.py              # Database check utility
├── add_test_package.py      # Utility for adding test packages
├── add_test_student.py      # Utility for adding test students
├── check_packages.py        # Utility for checking packages
└── test_email.py            # Utility for testing email functionality
```

## Development Tools
The repository includes several utility scripts to help with development:
- `add_test_package.py`: Add test packages to the database
- `add_test_student.py`: Add test student accounts
- `add_sample_packages.py`: Populate the database with sample packages
- `check_db.py`: Verify database connections and schema
- `check_packages.py`: Verify package records in the database
- `reset_migrations.py`: Reset database migrations
- `test_email.py`: Test email notification functionality

## Troubleshooting
- If database issues occur, try resetting migrations using `python reset_migrations.py`
- For email problems, test your configuration with `python test_email.py`
- Check environment variables with `python check_env.py`
