from flask import Flask, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from config import Config
import logging

db = SQLAlchemy()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    with app.app_context():
        try:
            logger.info("Creating database tables...")
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

            # Create tables but don't block if there's an issue
            try:
                db.create_all()
                logger.info("Database tables created successfully")
            except Exception as e:
                logger.error(f"Error creating database tables: {e}")
            
            # Register before_request hook to check if logged-in user is still active
            @app.before_request
            def check_user_active():
                if 'user_id' in session:
                    try:
                        user = User.query.get(session['user_id'])
                        if user and not user.is_active:
                            # User has been deactivated, log them out
                            session.clear()
                            flash('Your account has been deactivated.')
                            return redirect(url_for('auth.login'))
                    except Exception as e:
                        logger.error(f"Error checking user active status: {e}")

        except Exception as e:
            logger.error(f"Error during app initialization: {e}")
            raise

    return app

# Create app instance for Render deployment (fallback if gunicorn app:app is used)
app = create_app()