from app import app, db, Package
from datetime import datetime, timedelta

with app.app_context():
    # Count packages
    total_count = Package.query.count()
    
    if total_count == 0:
        print("No packages found in the database. Adding sample packages...")
        
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
        
        # Add packages to database
        db.session.add_all([package1, package2, package3])
        db.session.commit()
        
        print("Added 3 sample packages to the database.")
    else:
        # Count by category
        current_count = Package.query.filter_by(is_picked_up=False).count()
        picked_up_count = Package.query.filter_by(is_picked_up=True).count()
        
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        overdue_count = Package.query.filter(
            Package.is_picked_up == False,
            Package.date_received < seven_days_ago
        ).count()
        
        print(f"Package counts:")
        print(f"- Total: {total_count}")
        print(f"- Current (not picked up): {current_count}")
        print(f"- Picked up: {picked_up_count}")
        print(f"- Overdue (not picked up, older than 7 days): {overdue_count}")
        
        # List all packages
        packages = Package.query.all()
        print("\nPackages in database:")
        for pkg in packages:
            status = "Picked Up" if pkg.is_picked_up else "In Mail Room"
            date = pkg.date_received.strftime("%Y-%m-%d")
            print(f"ID: {pkg.id}, Recipient: {pkg.recipient_name}, Status: {status}, Date: {date}") 