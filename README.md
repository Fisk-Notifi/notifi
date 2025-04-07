# Notifi App

## Setup and Installation

1. Clone the repository:
```bash
git clone [repository-url]
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

4. Create a .env file in the root directory with the following variables: 
```
DATABASE_URL=sqlite:///database.db
SECRET_KEY=your_secret_key_here
```

5. Initialize the database:
```bash
flask db init
flask db migrate
flask db upgrade
```

6. Run the application:
```bash
python v/app.py
```

The application will be available at `http://localhost:5000`

## Features
- User authentication (signup/login) with Fisk email addresses
- QR code scanning functionality