from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app import db
from app.models import User, Vendor, Boat, Booking, Payment, Review
from sqlalchemy.orm import joinedload
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash

admin_bp = Blueprint('admin', __name__)

def login_required(f):
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

def admin_only(f):
    def wrapper(*args, **kwargs):
        if session.get('role') != 'admin':
            flash('Access denied')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

@admin_bp.route('/dashboard')
@login_required
@admin_only
def dashboard():
    total_users = User.query.filter_by(role='user').count()
    total_vendors = Vendor.query.count()
    total_boats = Boat.query.count()
    total_bookings = Booking.query.count()
    total_payments = Payment.query.filter_by(status='success').count()

    # Average rating
    reviews = Review.query.all()
    avg_rating = sum(review.rating for review in reviews) / len(reviews) if reviews else 0

    # Get Recent Activity - fetch latest bookings, reviews, and boats
    recent_activity = []
    
    # Get latest bookings
    latest_bookings = Booking.query.order_by(Booking.created_at.desc()).limit(5).all()
    for booking in latest_bookings:
        recent_activity.append({
            'type': 'booking',
            'title': f'Booking #{booking.id} - {booking.boat.name}',
            'description': f'User: {booking.user.username}',
            'timestamp': booking.created_at,
            'icon_class': 'fas fa-calendar-check',
            'color': 'blue'
        })
    
    # Get latest reviews
    latest_reviews = Review.query.order_by(Review.created_at.desc()).limit(5).all()
    for review in latest_reviews:
        recent_activity.append({
            'type': 'review',
            'title': f'Review - {review.boat.name}',
            'description': f'{review.user.username} - {review.rating}⭐',
            'timestamp': review.created_at,
            'icon_class': 'fas fa-star',
            'color': 'yellow'
        })
    
    # Get latest boats
    latest_boats = Boat.query.order_by(Boat.created_at.desc()).limit(5).all()
    for boat in latest_boats:
        recent_activity.append({
            'type': 'boat',
            'title': f'New Boat - {boat.name}',
            'description': f'Added by {boat.vendor.business_name}',
            'timestamp': boat.created_at,
            'icon_class': 'fas fa-ship',
            'color': 'green'
        })
    
    # Get latest users
    latest_users = User.query.filter_by(role='user').order_by(User.created_at.desc()).limit(5).all()
    for user in latest_users:
        recent_activity.append({
            'type': 'user',
            'title': f'New User - {user.username}',
            'description': user.email,
            'timestamp': user.created_at,
            'icon_class': 'fas fa-user-plus',
            'color': 'purple'
        })
    
    # Sort by timestamp descending and limit to 5 recent activities
    recent_activity.sort(key=lambda x: x['timestamp'], reverse=True)
    recent_activity = recent_activity[:5]

    return render_template('admin/dashboard.html',
                          total_users=total_users,
                          total_vendors=total_vendors,
                          total_boats=total_boats,
                          total_bookings=total_bookings,
                          total_payments=total_payments,
                          avg_rating=avg_rating,
                          recent_activity=recent_activity,
                          now=datetime.utcnow)

@admin_bp.route('/manage_vendors')
@login_required
@admin_only
def manage_vendors():
    vendors = Vendor.query.all()
    return render_template('admin/manage_vendors.html', vendors=vendors)

@admin_bp.route('/approve_vendor/<int:vendor_id>')
@login_required
@admin_only
def approve_vendor(vendor_id):
    vendor = Vendor.query.get_or_404(vendor_id)
    vendor.approved = True
    db.session.commit()
    flash('Vendor approved')
    return redirect(url_for('admin.manage_vendors'))

@admin_bp.route('/block_vendor/<int:vendor_id>')
@login_required
@admin_only
def block_vendor(vendor_id):
    vendor = Vendor.query.get_or_404(vendor_id)
    vendor.approved = False
    db.session.commit()
    flash('Vendor blocked')
    return redirect(url_for('admin.manage_vendors'))

@admin_bp.route('/manage_users')
@login_required
@admin_only
def manage_users():
    users = User.query.filter_by(role='user').all()
    return render_template('admin/manage_users.html', users=users)

@admin_bp.route('/manage_boats')
@login_required
@admin_only
def manage_boats():
    boats = Boat.query.options(joinedload(Boat.vendor)).all()
    return render_template('admin/manage_boats.html', boats=boats)

@admin_bp.route('/delete_boat/<int:boat_id>', methods=['DELETE'])
@login_required
@admin_only
def delete_boat(boat_id):
    boat = Boat.query.get_or_404(boat_id)
    
    try:
        # Delete all bookings associated with this boat
        Booking.query.filter_by(boat_id=boat_id).delete()
        
        # Delete all reviews associated with this boat
        Review.query.filter_by(boat_id=boat_id).delete()
        
        # Delete the boat
        db.session.delete(boat)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Boat deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_bp.route('/edit_boat/<int:boat_id>', methods=['GET', 'POST'])
@login_required
@admin_only
def edit_boat(boat_id):
    boat = Boat.query.get_or_404(boat_id)
    
    if request.method == 'POST':
        boat.name = request.form.get('name')
        boat.description = request.form.get('description')
        boat.location = request.form.get('location')
        boat.capacity = int(request.form.get('capacity', 0))
        boat.price_per_hour = float(request.form.get('price_per_hour', 0))
        boat.price_per_day = float(request.form.get('price_per_day', 0))
        
        try:
            db.session.commit()
            flash('Boat updated successfully', 'success')
            return redirect(url_for('admin.manage_boats'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating boat: {str(e)}', 'error')
    
    return render_template('admin/edit_boat.html', boat=boat)

@admin_bp.route('/moderate_reviews')
@login_required
@admin_only
def moderate_reviews():
    reviews = Review.query.all()
    return render_template('admin/moderate_reviews.html', reviews=reviews)

@admin_bp.route('/delete_review/<int:review_id>')
@login_required
@admin_only
def delete_review(review_id):
    review = Review.query.get_or_404(review_id)
    db.session.delete(review)
    db.session.commit()
    flash('Review deleted')
    return redirect(url_for('admin.moderate_reviews'))

@admin_bp.route('/all_bookings')
@login_required
@admin_only
def all_bookings():
    # Auto-complete expired approved bookings
    from datetime import datetime
    expired_bookings = Booking.query.filter_by(status='approved').filter(Booking.end_date < datetime.utcnow()).all()
    for booking in expired_bookings:
        booking.status = 'completed'
        db.session.commit()

    bookings = Booking.query.all()
    
    # Calculate statistics
    total_bookings = len(bookings)
    completed_bookings = len([b for b in bookings if b.status == 'completed'])
    pending_bookings = len([b for b in bookings if b.status == 'pending'])
    total_revenue = sum(b.total_price for b in bookings if b.status == 'completed')
    
    return render_template('admin/all_bookings.html', 
                         bookings=bookings,
                         total_bookings=total_bookings,
                         completed_bookings=completed_bookings,
                         pending_bookings=pending_bookings,
                         total_revenue=total_revenue)

@admin_bp.route('/approve_booking/<int:booking_id>')
@login_required
@admin_only
def approve_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    booking.status = 'approved'
    db.session.commit()
    flash('Booking approved successfully')
    return redirect(url_for('admin.all_bookings'))

@admin_bp.route('/reject_booking/<int:booking_id>')
@login_required
@admin_only
def reject_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    booking.status = 'rejected'
    db.session.commit()
    flash('Booking rejected')
    return redirect(url_for('admin.all_bookings'))

@admin_bp.route('/complete_booking/<int:booking_id>')
@login_required
@admin_only
def complete_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.status == 'approved':
        booking.status = 'completed'
        db.session.commit()
        flash('Booking marked as completed')
    else:
        flash('Only approved bookings can be marked as completed')
    return redirect(url_for('admin.all_bookings'))

@admin_bp.route('/deactivate_user/<int:user_id>', methods=['POST'])
@login_required
@admin_only
def deactivate_user(user_id):
    user = User.query.get_or_404(user_id)
    
    try:
        user.is_active = False
        db.session.commit()
        return jsonify({'success': True, 'message': 'User deactivated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_bp.route('/activate_user/<int:user_id>', methods=['POST'])
@login_required
@admin_only
def activate_user(user_id):
    user = User.query.get_or_404(user_id)
    
    try:
        user.is_active = True
        db.session.commit()
        return jsonify({'success': True, 'message': 'User activated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/change-password', methods=['POST'])
@login_required
@admin_only
def change_password():
    user = User.query.get(session['user_id'])

    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')

    # Validate current password
    if not check_password_hash(user.password_hash, current_password):
        flash('Current password is incorrect', 'error')
        return redirect(url_for('admin.dashboard'))

    # Validate new password
    if len(new_password) < 6:
        flash('New password must be at least 6 characters', 'error')
        return redirect(url_for('admin.dashboard'))

    # Check if passwords match
    if new_password != confirm_password:
        flash('New passwords do not match', 'error')
        return redirect(url_for('admin.dashboard'))

    # Check if new password is same as current password
    if check_password_hash(user.password_hash, new_password):
        flash('New password must be different from current password', 'error')
        return redirect(url_for('admin.dashboard'))

    # Update password
    user.password_hash = generate_password_hash(new_password)
    db.session.commit()

    flash('Password changed successfully', 'password')
    return redirect(url_for('admin.dashboard'))