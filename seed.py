"""
Database seeding script for Boat Booking System
Run with: python seed.py
"""

import os
import sys
from datetime import datetime, timedelta

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, Vendor, Boat, BoatImage, Booking, Review, Payment
import random

# Initialize app
app = create_app()

def seed_database():
    """Seed the database with sample data"""
    with app.app_context():
        # Clear existing data
        print("Clearing existing data...")
        db.drop_all()
        db.create_all()
        
        # Create Admin User
        print("Creating admin user...")
        admin = User(
            username='admin',
            email='admin@boatbooking.com',
            role='admin',
            is_active=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        
        # Create Regular Users
        print("Creating 5 regular users...")
        users = []
        user_data = [
            {'username': 'kiran', 'email': 'kiran@gmail.com'},
            {'username': 'Saro', 'email': 'saro@gmail.com'},
            {'username': 'Sachin', 'email': 'sachin@gmail.com'},
            {'username': 'akash', 'email': 'akash@gmail.com'},
            {'username': 'abdul', 'email': 'abdul@gmail.com'},
        ]
        
        for data in user_data:
            user = User(
                username=data['username'],
                email=data['email'],
                role='user',
                is_active=True
            )
            user.set_password('password123')
            db.session.add(user)
            users.append(user)
        
        db.session.commit()
        print(f"✓ Created {len(users)} users")
        
        # Create Vendors
        print("Creating 5 vendors...")
        vendors = []
        vendor_data = [
            {'username': 'vendor1', 'email': 'vendor1@example.com', 'business': 'Marina Deluxe', 'location': 'Goa'},
            {'username': 'vendor2', 'email': 'vendor2@example.com', 'business': 'Beach Boats Co', 'location': 'Kerala'},
            {'username': 'vendor3', 'email': 'vendor3@example.com', 'business': 'River Sports', 'location': 'Maharashtra'},
            {'username': 'vendor4', 'email': 'vendor4@example.com', 'business': 'Yacht Rentals', 'location': 'Gujarat'},
            {'username': 'vendor5', 'email': 'vendor5@example.com', 'business': 'Island Tours', 'location': 'Andaman'},
        ]
        
        for data in vendor_data:
            user = User(
                username=data['username'],
                email=data['email'],
                role='vendor',
                is_active=True
            )
            user.set_password('vendor123')
            db.session.add(user)
            db.session.flush()
            
            vendor = Vendor(
                user_id=user.id,
                business_name=data['business'],
                location=data['location'],
                approved=True
            )
            db.session.add(vendor)
            vendors.append(vendor)
        
        db.session.commit()
        print(f"✓ Created {len(vendors)} vendors")
        
        # Boat Categories - From dropdown filter options
        boat_categories = [
            {'name': 'Speed Boat', 'desc': 'High-speed performance boat', 'capacity': 8, 'price_hour': 1500, 'price_day': 8000},
            {'name': 'Luxury Yacht', 'desc': 'Luxurious yacht for premium experience', 'capacity': 12, 'price_hour': 3000, 'price_day': 15000},
            {'name': 'Fishing Boat', 'desc': 'Equipped for fishing expeditions', 'capacity': 6, 'price_hour': 800, 'price_day': 4500},
            {'name': 'Houseboat', 'desc': 'Comfortable houseboat for accommodation', 'capacity': 10, 'price_hour': 2000, 'price_day': 10000},
            {'name': 'Party Boat', 'desc': 'Perfect for celebrations and groups', 'capacity': 15, 'price_hour': 1800, 'price_day': 9000},
            {'name': 'Tour Boat', 'desc': 'Great for sightseeing tours', 'capacity': 12, 'price_hour': 1200, 'price_day': 6500},
            {'name': 'Diving Boat', 'desc': 'Equipped for diving and snorkeling', 'capacity': 8, 'price_hour': 1600, 'price_day': 8500},
        ]
        
        # Create Boats for each vendor (all categories for each vendor)
        print("Creating boats for vendors (all categories for each vendor)...")
        boats = []
        boat_counter = 1
        
        for vendor_idx, vendor in enumerate(vendors):
            for cat_data in boat_categories:
                boat = Boat(
                    vendor_id=vendor.id,
                    name=f"{cat_data['name']} {boat_counter}",
                    category=cat_data['name'],
                    location=vendor.location,
                    description=f"{cat_data['desc']} located at {vendor.location}. Professional crew, safety equipment, and full amenities provided.",
                    capacity=cat_data['capacity'],
                    price_per_hour=cat_data['price_hour'],
                    price_per_day=cat_data['price_day'],
                )
                db.session.add(boat)
                boats.append(boat)
                boat_counter += 1
        
        db.session.commit()
        print(f"✓ Created {len(boats)} boats ({len(boat_categories)} categories x {len(vendors)} vendors)")
        
        # Add boat images
        print("Adding boat images...")
        image_paths = [
            'boat_1.jpg', 'boat_2.jpg', 'boat_3.jpg', 'boat_4.jpg', 'boat_5.jpg',
            'boat_6.jpg', 'boat_7.jpg', 'boat_8.jpg', 'boat_9.jpg', 'diplomat.webp'
        ]
        
        for boat_idx, boat in enumerate(boats):
            image = BoatImage(
                boat_id=boat.id,
                image_path=image_paths[boat_idx % len(image_paths)]
            )
            db.session.add(image)
        
        db.session.commit()
        print(f"✓ Added images for {len(boats)} boats")
        
        # Create Bookings (mix of completed and active)
        print("Creating bookings (completed and active)...")
        bookings = []
        
        for user_idx, user in enumerate(users):
            # 2 completed bookings + 1 active booking per user
            for boat_idx in range(3):
                boat = boats[(user_idx * 3 + boat_idx) % len(boats)]
                
                if boat_idx < 2:  # Completed bookings
                    start_date = datetime.utcnow() - timedelta(days=30 - (boat_idx * 10))
                    end_date = start_date + timedelta(hours=8)
                    status = 'completed'
                else:  # Active booking
                    start_date = datetime.utcnow() + timedelta(days=5 + (boat_idx * 2))
                    end_date = start_date + timedelta(hours=6)
                    status = 'approved'
                
                total_price = (end_date - start_date).total_seconds() / 3600 * boat.price_per_hour
                
                booking = Booking(
                    user_id=user.id,
                    boat_id=boat.id,
                    start_date=start_date,
                    end_date=end_date,
                    total_price=total_price,
                    status=status
                )
                db.session.add(booking)
                bookings.append(booking)
        
        db.session.commit()
        print(f"✓ Created {len(bookings)} bookings")
        
        # Create Payments for all bookings
        print("Creating payment records...")
        payment_counter = 0
        for booking in bookings:
            payment = Payment(
                booking_id=booking.id,
                amount=booking.total_price,
                method=random.choice(['card', 'upi', 'wallet']),
                transaction_id=f'DEMO-{booking.id}-{random.randint(100000, 999999)}',
                status='success'
            )
            db.session.add(payment)
            payment_counter += 1
        
        db.session.commit()
        print(f"✓ Created {payment_counter} payment records")
        
        # Create Reviews for completed bookings only
        print("Creating reviews for completed bookings...")
        reviews = []
        review_comments = [
            "Amazing experience! Highly recommended!",
            "Great service and clean boat. Will book again.",
            "Best boat rental experience ever!",
            "Professional crew and beautiful boat.",
            "Fantastic day out on the water!",
            "Exceeded expectations. Five stars!",
            "Perfect for family outing. Great value for money.",
            "Wonderful experience. Boat was well maintained.",
        ]
        
        ratings = [5, 4, 5, 4, 5, 5, 4, 5]
        
        review_counter = 0
        for booking in bookings:
            if booking.status == 'completed':
                review = Review(
                    booking_id=booking.id,
                    user_id=booking.user_id,
                    boat_id=booking.boat_id,
                    rating=ratings[review_counter % len(ratings)],
                    review_text=review_comments[review_counter % len(review_comments)],
                    is_active=True,
                    created_at=booking.end_date + timedelta(hours=1)
                )
                db.session.add(review)
                reviews.append(review)
                review_counter += 1
        
        db.session.commit()
        print(f"✓ Created {len(reviews)} reviews")
        
        # Summary
        print("\n" + "="*70)
        print("DATABASE SEEDING COMPLETED SUCCESSFULLY!")
        print("="*70)
        print(f"\nData Summary:")
        print(f"  • Admin User: 1")
        print(f"  • Regular Users: {len(users)}")
        print(f"  • Vendors: {len(vendors)}")
        print(f"  • Boats: {len(boats)} (8 realistic categories per vendor)")
        print(f"  • Bookings: {len(bookings)} (Completed: {sum(1 for b in bookings if b.status == 'completed')}, Active: {sum(1 for b in bookings if b.status == 'approved')})")
        print(f"  • Reviews: {len(reviews)}")
        print(f"  • Payments: {payment_counter}")
        print(f"\n✓ All categories are realistic and match actual boat booking use cases")
        print(f"✓ Login credentials: See LOGIN_DETAILS.md")
        print("="*70 + "\n")

if __name__ == '__main__':
    seed_database()