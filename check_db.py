from app import app, db
from sqlalchemy import inspect

with app.app_context():
    # Create an inspector
    inspector = inspect(db.engine)

    # Get all table names
    table_names = inspector.get_table_names()
    print("Tables in database:")
    for table_name in table_names:
        print(f"\nTable: {table_name}")
        # Get columns for each table
        columns = inspector.get_columns(table_name)
        print("Columns:")
        for column in columns:
            print(f"  - {column['name']}: {column['type']}") 