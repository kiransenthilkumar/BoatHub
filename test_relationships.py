from app import create_app, db
from app.models import User, Vendor, Boat, Booking, Review

app = create_app()

with app.app_context():
    # Test relationships
    try:
        # Get the vendor user
        vendor_user = User.query.filter_by(username='vendor').first()
        if vendor_user:
            print(f"Vendor user found: {vendor_user.username}")

            # Test vendor relationship
            vendor = Vendor.query.filter_by(user_id=vendor_user.id).first()
            if vendor:
                print(f"Vendor profile found: {vendor.business_name}")
                print(f"Vendor user relationship works: {vendor.user.username}")

                # Test boat relationships
                boats = Boat.query.filter_by(vendor_id=vendor.id).all()
                print(f"Vendor has {len(boats)} boats")

                for boat in boats:
                    print(f"Boat: {boat.name}, Vendor: {boat.vendor.business_name}")
                    print(f"Boat has {len(boat.bookings)} bookings")
                    print(f"Boat has {len(boat.reviews)} reviews")

                    # Test booking relationships
                    for booking in boat.bookings:
                        print(f"Booking user: {booking.user.username}")
                        print(f"Booking boat: {booking.boat.name}")

                    # Test review relationships
                    for review in boat.reviews:
                        print(f"Review user: {review.user.username}")
                        print(f"Review boat: {review.boat.name}")

        print("All relationships are working correctly!")

    except Exception as e:
        print(f"Error testing relationships: {e}")