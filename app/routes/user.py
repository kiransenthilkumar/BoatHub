from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_file
from app import db
from app.models import User, Boat, BoatImage, Booking, Payment, Review
from datetime import datetime
from reportlab.pdfgen import canvas
from io import BytesIO
import random
from sqlalchemy.orm import joinedload
from werkzeug.security import check_password_hash, generate_password_hash

user_bp = Blueprint('user', __name__)

def login_required(f):
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

def user_only(f):
    def wrapper(*args, **kwargs):
        if session.get('role') != 'user':
            flash('Access denied')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

@user_bp.route('/dashboard')
@login_required
@user_only
def dashboard():
    # Auto-complete expired approved bookings for this user
    from datetime import datetime
    expired_bookings = Booking.query.filter_by(user_id=session['user_id'], status='approved').filter(Booking.end_date < datetime.utcnow()).all()
    for booking in expired_bookings:
        booking.status = 'completed'
        db.session.commit()

    user = User.query.get(session['user_id'])
    bookings = Booking.query.filter_by(user_id=user.id).options(db.joinedload(Booking.boat)).all()
    
    # Load images for each boat in bookings
    for booking in bookings:
        if booking.boat:
            booking.boat.images = BoatImage.query.filter_by(boat_id=booking.boat.id).all()
    
    # Calculate statistics
    active_bookings = [b for b in bookings if b.status in ['pending', 'approved']]
    completed_bookings = [b for b in bookings if b.status == 'completed']
    total_spent = sum(b.total_price for b in completed_bookings)
    
    return render_template('user/dashboard.html', 
                         user=user, 
                         bookings=bookings,
                         active_bookings=active_bookings,
                         completed_bookings=completed_bookings,
                         total_spent=total_spent)

@user_bp.route('/boats')
@login_required
@user_only
def boats():
    location = request.args.get('location')
    category = request.args.get('category')
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')
    capacity = request.args.get('capacity')
    min_rating = request.args.get('min_rating')
    sort_by = request.args.get('sort_by', 'featured')

    query = Boat.query

    if location:
        query = query.filter(Boat.location.ilike(f'%{location}%'))
    if category:
        query = query.filter(Boat.category == category)
    if min_price:
        query = query.filter(Boat.price_per_hour >= float(min_price))
    if max_price:
        query = query.filter(Boat.price_per_hour <= float(max_price))
    if capacity:
        query = query.filter(Boat.capacity >= int(capacity))

    boats = query.options(joinedload(Boat.vendor)).all()
    
    # Filter by rating in Python since average_rating is a property
    if min_rating:
        min_rating_float = float(min_rating)
        boats = [boat for boat in boats if boat.average_rating >= min_rating_float]
    
    # Apply sorting
    if sort_by == 'price_low':
        boats = sorted(boats, key=lambda b: b.price_per_hour)
    elif sort_by == 'price_high':
        boats = sorted(boats, key=lambda b: b.price_per_hour, reverse=True)
    elif sort_by == 'rating':
        boats = sorted(boats, key=lambda b: b.average_rating, reverse=True)
    elif sort_by == 'newest':
        boats = sorted(boats, key=lambda b: b.created_at, reverse=True)
    # 'featured' is default (no change needed)
    
    return render_template('user/boats.html', boats=boats, sort_by=sort_by)

@user_bp.route('/boat/<int:boat_id>')
@login_required
@user_only
def boat_detail(boat_id):
    boat = Boat.query.options(db.joinedload(Boat.vendor)).get_or_404(boat_id)
    reviews = Review.query.filter_by(boat_id=boat_id).order_by(Review.created_at.desc()).limit(5).all()
    return render_template('user/boat_detail.html', boat=boat, reviews=reviews)

@user_bp.route('/book/<int:boat_id>', methods=['GET', 'POST'])
@login_required
@user_only
def book_boat(boat_id):
    boat = Boat.query.get_or_404(boat_id)
    if request.method == 'POST':
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%dT%H:%M')
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%dT%H:%M')
        booking_type = request.form['booking_type']  # hourly or daily

        if booking_type == 'hourly':
            hours = (end_date - start_date).total_seconds() / 3600
            total_price = hours * boat.price_per_hour
        else:
            days = (end_date - start_date).days
            total_price = days * boat.price_per_day

        booking = Booking(
            user_id=session['user_id'],
            boat_id=boat_id,
            start_date=start_date,
            end_date=end_date,
            total_price=total_price
        )
        db.session.add(booking)
        db.session.commit()

        return redirect(url_for('user.payment', booking_id=booking.id))

    return render_template('user/book_boat.html', boat=boat)

@user_bp.route('/payment/<int:booking_id>', methods=['GET', 'POST'])
@login_required
@user_only
def payment(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != session['user_id']:
        flash('Access denied')
        return redirect(url_for('user.dashboard'))

    if request.method == 'POST':
        method = request.form['method']
        # Mock payment logic - For demo purposes, always succeed
        # success = random.choice([True, True, True, True, False])  # 80% success rate
        success = True  # Always succeed for demo

        if success:
            status = 'success'
            transaction_id = f'MOCKPAY-2026-{random.randint(100000, 999999)}'
            # Booking status remains 'pending' - requires admin approval
            # booking.status = 'approved'  # Commented out for admin approval system
        else:
            status = 'failed'
            transaction_id = f'MOCKPAY-2026-{random.randint(100000, 999999)}'

        payment = Payment(
            booking_id=booking_id,
            amount=booking.total_price,
            method=method,
            transaction_id=transaction_id,
            status=status
        )
        db.session.add(payment)
        db.session.commit()

        if status == 'success':
            return redirect(url_for('user.payment_success', booking_id=booking_id))
        else:
            return redirect(url_for('user.payment_failure', booking_id=booking_id))

    return render_template('user/payment.html', booking=booking)

@user_bp.route('/payment_success/<int:booking_id>')
@login_required
@user_only
def payment_success(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    return render_template('user/payment_success.html', booking=booking)

@user_bp.route('/payment_failure/<int:booking_id>')
@login_required
@user_only
def payment_failure(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    return render_template('user/payment_failure.html', booking=booking)

@user_bp.route('/booking_history')
@login_required
@user_only
def booking_history():
    # Auto-complete expired approved bookings for this user
    from datetime import datetime
    expired_bookings = Booking.query.filter_by(user_id=session['user_id'], status='approved').filter(Booking.end_date < datetime.utcnow()).all()
    for booking in expired_bookings:
        booking.status = 'completed'
        db.session.commit()

    bookings = Booking.query.filter_by(user_id=session['user_id']).options(db.joinedload(Booking.boat)).all()
    
    # Load images for each boat in bookings
    for booking in bookings:
        if booking.boat:
            booking.boat.images = BoatImage.query.filter_by(boat_id=booking.boat.id).all()
    
    # Calculate statistics
    active_bookings = [b for b in bookings if b.status in ['pending', 'approved']]
    completed_bookings = [b for b in bookings if b.status == 'completed']
    cancelled_bookings = [b for b in bookings if b.status in ['cancelled', 'rejected']]
    total_spent = sum(b.total_price for b in completed_bookings)
    
    return render_template('user/booking_history.html', 
                         bookings=bookings,
                         active_bookings=active_bookings,
                         completed_bookings=completed_bookings,
                         cancelled_bookings=cancelled_bookings,
                         total_spent=total_spent)

@user_bp.route('/cancel_booking/<int:booking_id>')
@login_required
@user_only
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != session['user_id']:
        flash('Access denied')
        return redirect(url_for('user.dashboard'))

    if booking.status in ['pending', 'approved']:
        booking.status = 'cancelled'
        db.session.commit()
        flash('Booking cancelled successfully')

    return redirect(url_for('user.booking_history'))

@user_bp.route('/review/<int:booking_id>', methods=['GET', 'POST'])
@login_required
@user_only
def review(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != session['user_id'] or booking.status != 'completed':
        flash('Access denied')
        return redirect(url_for('user.dashboard'))

    if Review.query.filter_by(booking_id=booking_id).first():
        flash('Review already submitted')
        return redirect(url_for('user.booking_history'))

    if request.method == 'POST':
        rating = int(request.form['rating'])
        review_text = request.form['review_text']

        review = Review(
            booking_id=booking_id,
            user_id=session['user_id'],
            boat_id=booking.boat_id,
            rating=rating,
            review_text=review_text
        )
        db.session.add(review)
        db.session.commit()

        flash('Review submitted successfully')
        return redirect(url_for('user.booking_history'))

    return render_template('user/review.html', booking=booking)

@user_bp.route('/profile')
@login_required
@user_only
def profile():
    user = User.query.get(session['user_id'])
    total_bookings = len(user.bookings)
    completed_bookings = len([b for b in user.bookings if b.status == 'completed'])
    return render_template('user/profile.html', user=user, total_bookings=total_bookings, completed_bookings=completed_bookings)

@user_bp.route('/change-password', methods=['POST'])
@login_required
@user_only
def change_password():
    user = User.query.get(session['user_id'])
    
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    # Validate current password
    if not check_password_hash(user.password_hash, current_password):
        flash('Current password is incorrect', 'error')
        return redirect(url_for('user.profile'))
    
    # Validate new password
    if len(new_password) < 6:
        flash('New password must be at least 6 characters', 'error')
        return redirect(url_for('user.profile'))
    
    # Check if passwords match
    if new_password != confirm_password:
        flash('New passwords do not match', 'error')
        return redirect(url_for('user.profile'))
    
    # Check if new password is same as current password
    if check_password_hash(user.password_hash, new_password):
        flash('New password must be different from current password', 'error')
        return redirect(url_for('user.profile'))
    
    # Update password
    user.password_hash = generate_password_hash(new_password)
    db.session.commit()
    
    flash('Password changed successfully', 'password')
    return redirect(url_for('user.profile'))