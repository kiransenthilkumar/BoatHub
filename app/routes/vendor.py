from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import db
from app.models import User, Vendor, Boat, BoatImage, Booking, Review
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
import os
from sqlalchemy.orm import joinedload
from datetime import datetime

vendor_bp = Blueprint('vendor', __name__)

def login_required(f):
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

def vendor_only(f):
    def wrapper(*args, **kwargs):
        if session.get('role') != 'vendor':
            flash('Access denied')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

@vendor_bp.route('/dashboard')
@login_required
@vendor_only
def dashboard():
    user = User.query.get(session['user_id'])
    vendor = Vendor.query.filter_by(user_id=user.id).first()
    if not vendor or not vendor.approved:
        flash('Your vendor account is not approved yet')
        return redirect(url_for('auth.login'))

    boats = Boat.query.filter_by(vendor_id=vendor.id).all()
    
    # Load images for each boat explicitly
    for boat in boats:
        boat.images = BoatImage.query.filter_by(boat_id=boat.id).all()
    
    bookings = []
    for boat in boats:
        boat_bookings = Booking.query.filter_by(boat_id=boat.id).options(db.joinedload(Booking.user)).all()
        bookings.extend(boat_bookings)

    earnings = sum(booking.total_price for booking in bookings if booking.status == 'completed')
    active_bookings = [b for b in bookings if b.status in ['pending', 'approved']]
    
    # Calculate average rating and total reviews
    total_reviews = 0
    total_rating_sum = 0
    for boat in boats:
        for review in boat.reviews:
            if review.rating:
                total_reviews += 1
                total_rating_sum += review.rating
    
    avg_rating = total_rating_sum / total_reviews if total_reviews > 0 else 0
    
    # Calculate occupancy rate
    total_booking_days = 0
    occupied_days = 0
    for booking in bookings:
        if booking.status == 'completed':
            booking_days = (booking.end_date - booking.start_date).days + 1
            total_booking_days += booking_days
            occupied_days += booking_days
    
    # Calculate total possible days (assuming 30 days per month for simplicity)
    total_possible_days = len(boats) * 30  # 30 days per boat
    occupancy_rate = (occupied_days / total_possible_days * 100) if total_possible_days > 0 else 0
    
    return render_template('vendor/dashboard.html', 
                         vendor=vendor, 
                         boats=boats, 
                         bookings=bookings, 
                         earnings=earnings,
                         active_bookings=active_bookings,
                         avg_rating=avg_rating,
                         total_reviews=total_reviews,
                         occupancy_rate=occupancy_rate)

@vendor_bp.route('/add_boat', methods=['GET', 'POST'])
@login_required
@vendor_only
def add_boat():
    user = User.query.get(session['user_id'])
    vendor = Vendor.query.filter_by(user_id=user.id).first()

    if request.method == 'POST':
        name = request.form['name']
        location = request.form['location']
        category = request.form['category']
        price_per_hour = float(request.form['price_per_hour'])
        price_per_day = float(request.form['price_per_day'])
        capacity = int(request.form['capacity'])
        description = request.form['description']

        boat = Boat(
            vendor_id=vendor.id,
            name=name,
            location=location,
            category=category,
            price_per_hour=price_per_hour,
            price_per_day=price_per_day,
            capacity=capacity,
            description=description
        )
        db.session.add(boat)
        db.session.commit()

        # Handle image uploads
        images = request.files.getlist('images')
        for image in images:
            if image:
                filename = secure_filename(image.filename)
                image_path = os.path.join('app', 'static', 'images', filename)
                image.save(image_path)
                boat_image = BoatImage(boat_id=boat.id, image_path=filename)
                db.session.add(boat_image)
        db.session.commit()

        flash('Boat added successfully')
        return redirect(url_for('vendor.dashboard'))

    return render_template('vendor/add_boat.html')

@vendor_bp.route('/manage_bookings')
@login_required
@vendor_only
def manage_bookings():
    user = User.query.get(session['user_id'])
    vendor = Vendor.query.filter_by(user_id=user.id).first()
    boats = Boat.query.filter_by(vendor_id=vendor.id).all()
    bookings = []
    for boat in boats:
        bookings.extend(Booking.query.filter_by(boat_id=boat.id).all())

    return render_template('vendor/manage_bookings.html', bookings=bookings)

@vendor_bp.route('/approve_booking/<int:booking_id>')
@login_required
@vendor_only
def approve_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    user = User.query.get(session['user_id'])
    vendor = Vendor.query.filter_by(user_id=user.id).first()
    if booking.boat.vendor_id != vendor.id:
        flash('Access denied')
        return redirect(url_for('vendor.dashboard'))

    booking.status = 'approved'
    db.session.commit()
    flash('Booking approved')
    return redirect(url_for('vendor.manage_bookings'))

@vendor_bp.route('/reject_booking/<int:booking_id>')
@login_required
@vendor_only
def reject_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    user = User.query.get(session['user_id'])
    vendor = Vendor.query.filter_by(user_id=user.id).first()
    if booking.boat.vendor_id != vendor.id:
        flash('Access denied')
        return redirect(url_for('vendor.dashboard'))

    booking.status = 'rejected'
    db.session.commit()
    flash('Booking rejected')
    return redirect(url_for('vendor.manage_bookings'))

@vendor_bp.route('/reviews')
@login_required
@vendor_only
def reviews():
    user = User.query.get(session['user_id'])
    vendor = Vendor.query.filter_by(user_id=user.id).first()
    boats = Boat.query.filter_by(vendor_id=vendor.id).all()
    reviews = []
    for boat in boats:
        reviews.extend(Review.query.filter_by(boat_id=boat.id).all())
    
    # Calculate statistics
    total_reviews = len(reviews)
    total_rating_sum = sum(review.rating for review in reviews if review.rating)
    avg_rating = total_rating_sum / total_reviews if total_reviews > 0 else 0
    positive_reviews = len([r for r in reviews if r.rating and r.rating >= 4])
    
    return render_template('vendor/reviews.html', 
                         reviews=reviews,
                         avg_rating=avg_rating,
                         total_reviews=total_reviews,
                         positive_reviews=positive_reviews)

@vendor_bp.route('/my_boats')
@login_required
@vendor_only
def my_boats():
    user = User.query.get(session['user_id'])
    vendor = Vendor.query.filter_by(user_id=user.id).first()
    if not vendor or not vendor.approved:
        flash('Your vendor account is not approved yet')
        return redirect(url_for('auth.login'))
    boats = Boat.query.filter_by(vendor_id=vendor.id).all()
    
    # Load images for each boat explicitly
    for boat in boats:
        boat.images = BoatImage.query.filter_by(boat_id=boat.id).all()
    
    # Calculate statistics
    total_bookings = []
    active_bookings = []
    completed_bookings = []
    total_ratings = []
    
    for boat in boats:
        boat_bookings = Booking.query.filter_by(boat_id=boat.id).all()
        total_bookings.extend(boat_bookings)
        active_bookings.extend([b for b in boat_bookings if b.status in ['pending', 'approved']])
        completed_bookings.extend([b for b in boat_bookings if b.status == 'completed'])
        
        # Add active_bookings to boat object for template
        boat.active_bookings = [b for b in boat_bookings if b.status in ['pending', 'approved']]
        boat.total_bookings = boat_bookings
        
        # Collect ratings for overall statistics
        reviews = [r for r in boat.reviews if r.rating]
        total_ratings.extend([r.rating for r in reviews])
    
    # Calculate overall statistics
    avg_rating = sum(total_ratings) / len(total_ratings) if total_ratings else 0
    total_booking_count = len(total_bookings)
    occupancy_rate = (len(completed_bookings) / total_booking_count * 100) if total_booking_count > 0 else 0
    
    return render_template('vendor/my_boats.html', 
                         boats=boats,
                         active_bookings=active_bookings,
                         total_bookings=total_bookings,
                         avg_rating=avg_rating,
                         occupancy_rate=occupancy_rate)

@vendor_bp.route('/edit_boat/<int:boat_id>', methods=['GET', 'POST'])
@login_required
@vendor_only
def edit_boat(boat_id):
    user = User.query.get(session['user_id'])
    vendor = Vendor.query.filter_by(user_id=user.id).first()
    boat = Boat.query.get_or_404(boat_id)
    
    if boat.vendor_id != vendor.id:
        flash('Access denied')
        return redirect(url_for('vendor.dashboard'))

    if request.method == 'POST':
        boat.name = request.form['name']
        boat.location = request.form['location']
        boat.category = request.form['category']
        boat.price_per_hour = float(request.form['price_per_hour'])
        boat.price_per_day = float(request.form['price_per_day'])
        boat.capacity = int(request.form['capacity'])
        boat.description = request.form['description']
        db.session.commit()

        # Handle image uploads
        images = request.files.getlist('images')
        for image in images:
            if image:
                filename = secure_filename(image.filename)
                image_path = os.path.join('app', 'static', 'images', filename)
                image.save(image_path)
                boat_image = BoatImage(boat_id=boat.id, image_path=filename)
                db.session.add(boat_image)
        db.session.commit()

        flash('Boat updated successfully')
        return redirect(url_for('vendor.dashboard'))

    return render_template('vendor/edit_boat.html', boat=boat)

@vendor_bp.route('/delete_boat/<int:boat_id>', methods=['POST'])
@login_required
@vendor_only
def delete_boat(boat_id):
    user = User.query.get(session['user_id'])
    vendor = Vendor.query.filter_by(user_id=user.id).first()
    boat = Boat.query.get_or_404(boat_id)
    
    # Check if boat belongs to vendor
    if boat.vendor_id != vendor.id:
        flash('Access denied', 'error')
        return redirect(url_for('vendor.my_boats'))
    
    # Delete boat images from filesystem and database
    boat_images = BoatImage.query.filter_by(boat_id=boat.id).all()
    for image in boat_images:
        image_path = os.path.join('app', 'static', 'images', image.image_path)
        if os.path.exists(image_path):
            os.remove(image_path)
        # Delete image record from database
        db.session.delete(image)
    
    # Delete boat from database
    db.session.delete(boat)
    db.session.commit()
    
    flash('Boat deleted successfully', 'success')
    return redirect(url_for('vendor.my_boats'))

@vendor_bp.route('/delete_boat_image/<int:image_id>')
@login_required
@vendor_only
def delete_boat_image(image_id):
    user = User.query.get(session['user_id'])
    vendor = Vendor.query.filter_by(user_id=user.id).first()
    image = BoatImage.query.get_or_404(image_id)
    boat = Boat.query.get(image.boat_id)
    
    if boat.vendor_id != vendor.id:
        flash('Access denied')
        return redirect(url_for('vendor.dashboard'))

    # Delete the actual file
    image_path = os.path.join('app', 'static', 'images', image.image_path)
    if os.path.exists(image_path):
        os.remove(image_path)
    
    db.session.delete(image)
    db.session.commit()
    flash('Image deleted successfully')
    return redirect(url_for('vendor.edit_boat', boat_id=boat.id))

@vendor_bp.route('/profile')
@login_required
@vendor_only
def profile():
    user = User.query.get(session['user_id'])
    vendor = Vendor.query.filter_by(user_id=user.id).first()
    return render_template('vendor/profile.html', user=user, vendor=vendor, now=datetime.utcnow)


@vendor_bp.route('/change-password', methods=['POST'])
@login_required
@vendor_only
def change_password():
    user = User.query.get(session['user_id'])

    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')

    # Validate current password
    if not check_password_hash(user.password_hash, current_password):
        flash('Current password is incorrect', 'error')
        return redirect(url_for('vendor.profile'))

    # Validate new password
    if len(new_password) < 6:
        flash('New password must be at least 6 characters', 'error')
        return redirect(url_for('vendor.profile'))

    # Check if passwords match
    if new_password != confirm_password:
        flash('New passwords do not match', 'error')
        return redirect(url_for('vendor.profile'))

    # Check if new password is same as current password
    if check_password_hash(user.password_hash, new_password):
        flash('New password must be different from current password', 'error')
        return redirect(url_for('vendor.profile'))

    # Update password
    user.password_hash = generate_password_hash(new_password)
    db.session.commit()

    flash('Password changed successfully', 'password')
    return redirect(url_for('vendor.profile'))