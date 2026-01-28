from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')  # user, vendor, admin
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    bookings = db.relationship('Booking', backref='user', lazy=True)
    reviews = db.relationship('Review', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    business_name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    approved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref='vendor_profile', lazy=True)
    boats = db.relationship('Boat', backref='vendor', lazy=True)

class Boat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False, default='Speed Boat')
    price_per_hour = db.Column(db.Float, nullable=False)
    price_per_day = db.Column(db.Float, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    images = db.relationship('BoatImage', backref='boat', lazy=True)
    bookings = db.relationship('Booking', backref='boat', lazy=True)
    reviews = db.relationship('Review', backref='boat', lazy=True)

    @property
    def average_rating(self):
        reviews = Review.query.filter_by(boat_id=self.id).all()
        if not reviews:
            return 0
        return sum(review.rating for review in reviews) / len(reviews)

class BoatImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    boat_id = db.Column(db.Integer, db.ForeignKey('boat.id'), nullable=False)
    image_path = db.Column(db.String(200), nullable=False)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    boat_id = db.Column(db.Integer, db.ForeignKey('boat.id'), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, approved, rejected, completed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    payment = db.relationship('Payment', backref='booking', uselist=False)
    review = db.relationship('Review', backref='booking', uselist=False)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    method = db.Column(db.String(20), nullable=False)  # card, upi, wallet
    transaction_id = db.Column(db.String(50), unique=True, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, success, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    boat_id = db.Column(db.Integer, db.ForeignKey('boat.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    review_text = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)