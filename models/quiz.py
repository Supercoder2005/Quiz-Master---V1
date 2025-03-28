# from . import db
# from datetime import datetime

# class Quiz(db.Model):
#     __tablename__ = 'quizzes'
    
#     id = db.Column(db.Integer, primary_key=True)
#     chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'), nullable=False)
#     title = db.Column(db.String(100), nullable=False)
#     description = db.Column(db.Text)
#     date_of_quiz = db.Column(db.Date)
#     time_duration = db.Column(db.String(5))  # Format: HH:MM
#     remarks = db.Column(db.Text)
#     created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
#     # Relationships
#     questions = db.relationship('Question', backref='quiz', lazy=True, cascade="all, delete-orphan")
#     scores = db.relationship('Score', backref='quiz', lazy=True, cascade="all, delete-orphan") 

from . import db
from datetime import datetime

class Quiz(db.Model):
    __tablename__ = 'quizzes'
    
    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id', ondelete="CASCADE"), nullable=False, index=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    date_of_quiz = db.Column(db.Date, default=datetime.utcnow)  # Default to today if not specified
    time_duration = db.Column(db.Time)  # Changed from String to Time
    remarks = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    # Relationships
    questions = db.relationship('Question', backref='quiz', lazy=True, cascade="all, delete-orphan")
    scores = db.relationship('Score', backref='quiz', lazy=True, cascade="all, delete-orphan")
