from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import db
from app.models import User, Vendor, Boat, Booking, Review
from werkzeug.security import generate_password_hash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def home():
    """Landing page for the boat booking system"""
    total_boats = Boat.query.count()
    total_bookings = Booking.query.count()
    total_vendors = Vendor.query.count()
    
    # Get featured boats
    featured_boats = Boat.query.limit(6).all()
    
    # Get top-rated boats
    all_boats = Boat.query.all()
    top_rated_boats = sorted(all_boats, key=lambda b: b.average_rating, reverse=True)[:3]
    
    return render_template('landing.html',
                          total_boats=total_boats,
                          total_bookings=total_bookings,
                          total_vendors=total_vendors,
                          featured_boats=featured_boats,
                          top_rated_boats=top_rated_boats)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(email=email).first():
            flash('Email already exists')
            return redirect(url_for('auth.register'))

        user = User(username=username, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        if role == 'vendor':
            vendor = Vendor(user_id=user.id, business_name=request.form['business_name'], location=request.form['location'])
            db.session.add(vendor)
            db.session.commit()

        flash('Registration successful')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            # Check if user account is active
            if not user.is_active:
                flash('Your account has been deactivated. Please contact support.')
                return redirect(url_for('auth.login'))
            
            session['user_id'] = user.id
            session['role'] = user.role
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif user.role == 'vendor':
                return redirect(url_for('vendor.dashboard'))
            else:
                return redirect(url_for('user.dashboard'))
        else:
            flash('Invalid credentials')

    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))