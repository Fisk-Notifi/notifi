from app import app, db, Package
from datetime import datetime, timedelta

with app.app_context():
    # Create sample packages with different statuses and dates
    
    # Current package (not picked up, recent)
    package1 = Package(
        recipient_name="Alice Johnson",
        sender_name="Amazon",
        recipient_address="123 University Ave",
        date_received=datetime.utcnow() - timedelta(days=1),
        is_picked_up=False
    )
    
    # Picked up package
    package2 = Package(
        recipient_name="Bob Smith",
        sender_name="Family",
        recipient_address="456 Campus Dr",
        date_received=datetime.utcnow() - timedelta(days=3),
        is_picked_up=True,
        picked_up_date=datetime.utcnow() - timedelta(hours=12)
    )
    
    # Overdue package (not picked up, older than 7 days)
    package3 = Package(
        recipient_name="Charlie Brown",
        sender_name="eBay Seller",
        recipient_address="789 College St",
        date_received=datetime.utcnow() - timedelta(days=10),
        is_picked_up=False
    )
    
    # Another current package
    package4 = Package(
        recipient_name="Diana Prince",
        sender_name="Office Depot",
        recipient_address="101 Main St",
        date_received=datetime.utcnow() - timedelta(days=2),
        is_picked_up=False
    )
    
    # Another picked up package
    package5 = Package(
        recipient_name="Ethan Hunt",
        sender_name="Target",
        recipient_address="202 Oak Ave",
        date_received=datetime.utcnow() - timedelta(days=5),
        is_picked_up=True,
        picked_up_date=datetime.utcnow() - timedelta(days=1)
    )
    
    # Add packages to database
    db.session.add_all([package1, package2, package3, package4, package5])
    db.session.commit()
    
    print("Added 5 sample packages to the database.")
    
    # List all packages after adding
    packages = Package.query.all()
    print("\nPackages in database:")
    for pkg in packages:
        status = "Picked Up" if pkg.is_picked_up else "In Mail Room"
        date = pkg.date_received.strftime("%Y-%m-%d")
        print(f"ID: {pkg.id}, Recipient: {pkg.recipient_name}, Status: {status}, Date: {date}") 