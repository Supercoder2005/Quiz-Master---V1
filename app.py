from flask import Flask, redirect, url_for, session
from flask_login import LoginManager, current_user
from config import Config
from models import db
from models.user import User  # Ensure User model has an is_admin field

# Import controllers
from controllers.auth import auth
from controllers.admin import admin
from controllers.user import user

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # ✅ Set a secret key for session handling
    app.secret_key = "supersecretkey"  # Change this in production

    # Initialize database
    db.init_app(app)

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"  # Redirect to login if not authenticated

    # ✅ Store `is_admin` in the session when a user logs in
    @login_manager.user_loader
    def load_user(user_id):
        user = User.query.get(int(user_id))
        if user:
            session['is_admin'] = user.is_admin  # Store admin status in session
        return user

    # Register blueprints
    app.register_blueprint(auth)
    app.register_blueprint(admin)
    app.register_blueprint(user)

    # Create database tables and default admin user
    with app.app_context():
        db.create_all()
        User.create_admin()  # Create default admin user if not exists

    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))
    
    # ✅ Ensure only admins can access this route
    @app.route('/admin/dashboard')
    def admin_dashboard():
        if not session.get('is_admin'):  # Check if user is an admin
            return redirect(url_for('auth.login'))  # Redirect non-admins
        return redirect(url_for('admin.dashboard'))

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
