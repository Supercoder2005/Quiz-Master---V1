from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from . import db

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    qualification = db.Column(db.String(100))
    dob = db.Column(db.Date)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with scores
    scores = db.relationship('Score', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @staticmethod
    def create_admin():
        """Create an admin user if one doesn't exist"""
        admin = User.query.filter_by(is_admin=True).first()
        if not admin:
            admin = User(
                email='admin@quizmaster.com',
                full_name='Admin User',
                is_admin=True
            )
            admin.set_password('admin123')  # Default password
            db.session.add(admin)
            db.session.commit()
        return admin
