from app import app, db
from sqlalchemy import text

with app.app_context():
    # Drop the package table
    with db.engine.connect() as conn:
        conn.execute(text('DROP TABLE IF EXISTS package;'))
        conn.commit()
    print("Package table dropped successfully") 