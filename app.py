from flask import Flask, redirect, url_for
from config import Config
from models import db  # This should now work correctly
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