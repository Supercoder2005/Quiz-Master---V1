from flask import Flask, redirect, url_for
from flask_login import LoginManager
from config import Config
from models import db
from models.user import User

# Import controllers
from controllers.auth import auth
from controllers.admin import admin
from controllers.user import user

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize database
    db.init_app(app)

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"  # Redirect to login if not authenticated

    # Define user loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

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

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
