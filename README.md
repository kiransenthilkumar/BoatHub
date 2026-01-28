# Boat Booking System

A comprehensive boat booking web application built with Python Flask, SQLite, and Tailwind CSS for final year project submission.

## 🎯 Project Overview

This system allows users to browse, book, and review boats while vendors can manage their fleet and bookings. Admins oversee the entire platform with moderation capabilities.

## 🏗️ Architecture

### Database Schema

```sql
-- Users table
CREATE TABLE user (
    id INTEGER PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Vendors table
CREATE TABLE vendor (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    business_name VARCHAR(100) NOT NULL,
    location VARCHAR(100) NOT NULL,
    approved BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id)
);

-- Boats table
CREATE TABLE boat (
    id INTEGER PRIMARY KEY,
    vendor_id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    location VARCHAR(100) NOT NULL,
    price_per_hour FLOAT NOT NULL,
    price_per_day FLOAT NOT NULL,
    capacity INTEGER NOT NULL,
    description TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vendor_id) REFERENCES vendor(id)
);

-- Boat Images table
CREATE TABLE boat_image (
    id INTEGER PRIMARY KEY,
    boat_id INTEGER NOT NULL,
    image_path VARCHAR(200) NOT NULL,
    FOREIGN KEY (boat_id) REFERENCES boat(id)
);

-- Bookings table
CREATE TABLE booking (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    boat_id INTEGER NOT NULL,
    start_date DATETIME NOT NULL,
    end_date DATETIME NOT NULL,
    total_price FLOAT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (boat_id) REFERENCES boat(id)
);

-- Payments table
CREATE TABLE payment (
    id INTEGER PRIMARY KEY,
    booking_id INTEGER NOT NULL,
    amount FLOAT NOT NULL,
    method VARCHAR(20) NOT NULL,
    transaction_id VARCHAR(50) UNIQUE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES booking(id)
);

-- Reviews table
CREATE TABLE review (
    id INTEGER PRIMARY KEY,
    booking_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    boat_id INTEGER NOT NULL,
    rating INTEGER NOT NULL,
    review_text TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES booking(id),
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (boat_id) REFERENCES boat(id)
);
```

### Application Workflow

1. **User Registration/Login**: Users register with role selection
2. **Boat Browsing**: Filter by location, price, capacity, rating
3. **Booking Process**:
   - Select boat and dates
   - Proceed to mock payment
   - Payment success → booking confirmed
   - Payment failure → booking cancelled
4. **Review Submission**: Only after completed bookings
4. **Vendor Management**: Approve/reject bookings, view earnings, add/edit boats, manage images
6. **Admin Moderation**: Manage users, vendors, reviews

## 🚀 Deployment

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Remove existing database (if schema changes)
rm -f instance/boat_booking.db

# Seed the database with sample data
python -c "from seed import *"

# Run the application
python run.py
```

### Render Deployment

1. Create a Render account
2. Connect your GitHub repository
3. Use the provided `render.yaml` configuration
4. Set environment variables:
   - `SECRET_KEY`: Your secret key
   - `FLASK_ENV`: production

## 📋 Sample Data & Testing

### Login Credentials

After running `python seed.py`, you can use these accounts to test the system:

#### Admin Account
- **Username**: admin
- **Password**: admin123
- **Role**: Administrator (can manage users, vendors, and system-wide settings)

#### User Accounts
- **Username**: Saro | **Password**: password123
- **Username**: Kiran | **Password**: password123
- **Username**: Akash | **Password**: password123
- **Role**: Regular users (can browse boats, make bookings, and leave reviews)

#### Vendor Accounts
- **Username**: vendor1 | **Password**: vendor123 | **Business**: Chennai Boat Adventures
- **Username**: vendor2 | **Password**: vendor123 | **Business**: Kerala Backwater Tours
- **Username**: vendor3 | **Password**: vendor123 | **Business**: Goa Beach Rentals
- **Username**: vendor4 | **Password**: vendor123 | **Business**: Andaman Island Explorers
- **Role**: Boat vendors (can add, edit, and manage boats, handle bookings, view earnings)

**Navigation Features:**
- **Dashboard**: Overview with quick stats and recent bookings
- **My Boats**: Dedicated page to view and manage all boat listings
- **Add Boat**: Form to add new boats with categories and images
- **Manage Bookings**: Approve/reject bookings and track earnings
- **Profile**: Business information and account status

### Sample Boats Data

The system comes pre-loaded with 10 boats across South Indian locations and 7 categories:

#### Boat Categories:
- **Speed Boat**: High-speed boats for adventure
- **Luxury Yacht**: Premium yachts for special occasions
- **Fishing Boat**: Boats designed for fishing trips
- **Houseboat**: Traditional backwater houseboats
- **Party Boat**: Boats perfect for parties and celebrations
- **Tour Boat**: Boats for island and coastal tours
- **Diving Boat**: Specialized boats for diving expeditions

#### Chennai Marina (Vendor 1 - Chennai Boat Adventures)
1. **Speed Boat Chennai Express** - Speed Boat
2. **Luxury Yacht Marina Pride** - Luxury Yacht
3. **Fishing Boat Marina Fisher** - Fishing Boat

#### Alleppey (Vendor 2 - Kerala Backwater Tours)
4. **Backwater Houseboat Serenity** - Houseboat
5. **Speed Cruiser Kerala Wave** - Speed Boat

#### Goa (Vendor 3 - Goa Beach Rentals)
6. **Beach Party Boat Goa Fun** - Party Boat
7. **Luxury Catamaran Goa Paradise** - Luxury Yacht
8. **Speed Boat Goa Racer** - Speed Boat

#### Port Blair (Vendor 4 - Andaman Island Explorers)
9. **Island Explorer Andaman** - Tour Boat
10. **Diving Boat Coral Reef** - Diving Boat

## 📊 Diagrams

### ER Diagram
```
User (1) ──── (M) Vendor
  │              │
  │              │
  └─── (M) Booking (M) ─── Boat (1) ─── (M) BoatImage
           │              │
           │              │
           └── (1) Payment │
                          │
                          └── (M) Review
```

### DFD Level 0
```
[External Entities]
Users, Vendors, Admins

[Process]
Boat Booking System

[Data Stores]
User DB, Boat DB, Booking DB, Payment DB, Review DB

[Data Flows]
Registration, Login, Boat Search, Booking, Payment, Reviews
```

## 🎓 Viva Preparation

### Key Features Demonstrated

1. **Role-based Authentication**: Session-based with decorators
2. **Database Relationships**: Foreign keys and joins
3. **Mock Payment System**: Realistic transaction simulation with INR currency
4. **Review System**: One review per booking, average ratings
5. **File Upload**: Boat images with secure handling and editing
6. **Boat Management**: Vendors can add, edit, and manage boat listings
7. **Category System**: Boats organized by categories (Speed Boat, Luxury Yacht, etc.)
8. **Advanced Filtering**: Browse boats by location, category, price, capacity, and rating
9. **Image Management**: Upload multiple images and delete existing ones
10. **PDF Generation**: Booking receipts
11. **Responsive UI**: Tailwind CSS components

### Sample Viva Questions

**Q: How does the mock payment system work?**
A: The system simulates real payment processing with random success/failure outcomes, generating unique transaction IDs prefixed with "MOCKPAY-2026-".

**Q: Explain the review system constraints.**
A: Reviews can only be submitted after booking completion, one per booking, with 1-5 star ratings and text feedback.

**Q: How is role-based access control implemented?**
A: Using Flask session variables and custom decorators that check user roles before allowing access to protected routes.

### Project Advantages

- **Scalable Architecture**: Modular Flask blueprints
- **Secure**: Password hashing, input validation
- **User-friendly**: Responsive design, intuitive workflows
- **Real-world Ready**: Complete booking lifecycle
- **Educational Value**: Demonstrates full-stack concepts

### Future Enhancements

- Real payment gateway integration
- Real-time notifications
- Advanced search with maps
- Mobile app development
- Analytics dashboard
- Multi-language support

## 📝 Development Notes

- All templates use Tailwind CSS for consistent styling
- SQLite chosen for simplicity and deployment ease
- Session-based auth for state management
- Blueprint organization for maintainable code
- Mock payment demonstrates transaction flow concepts

## 🔧 Technologies Used

- **Backend**: Python Flask 2.3.3
- **Database**: SQLite with SQLAlchemy
- **Frontend**: HTML5, Jinja2, Tailwind CSS
- **Deployment**: Render with Gunicorn
- **Additional**: ReportLab (PDF), Pillow (images)

This project demonstrates industry-standard practices suitable for university evaluation and real-world deployment.