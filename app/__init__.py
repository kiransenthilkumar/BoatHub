from flask import Flask, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    with app.app_context():
        from . import routes
        from .models import User
        app.register_blueprint(routes.auth_bp, url_prefix='/auth')
        app.register_blueprint(routes.user_bp, url_prefix='/user')
        app.register_blueprint(routes.vendor_bp, url_prefix='/vendor')
        app.register_blueprint(routes.admin_bp, url_prefix='/admin')

        @app.route('/')
        def index():
            if 'user_id' in session:
                if session['role'] == 'admin':
                    return redirect(url_for('admin.dashboard'))
                elif session['role'] == 'vendor':
                    return redirect(url_for('vendor.dashboard'))
                else:
                    return redirect(url_for('user.dashboard'))
            return redirect(url_for('auth.home'))

        db.create_all()
        
        # Register before_request hook to check if logged-in user is still active
        @app.before_request
        def check_user_active():
            if 'user_id' in session:
                user = User.query.get(session['user_id'])
                if user and not user.is_active:
                    # User has been deactivated, log them out
                    session.clear()
                    flash('Your account has been deactivated.')
                    return redirect(url_for('auth.login'))

    return app

# Create app instance for Render deployment (fallback if gunicorn app:app is used)
app = create_app()