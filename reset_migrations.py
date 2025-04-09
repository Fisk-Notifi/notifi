from app import app, db
from sqlalchemy import text

with app.app_context():
    # Drop the alembic_version table
    with db.engine.connect() as conn:
        conn.execute(text('DROP TABLE IF EXISTS alembic_version;'))
        conn.commit()
    print("Alembic version table dropped successfully") 