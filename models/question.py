# from . import db

# class Question(db.Model):
#     __tablename__ = 'questions'
    
#     id = db.Column(db.Integer, primary_key=True)
#     quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
#     question_statement = db.Column(db.Text, nullable=False)
#     option1 = db.Column(db.Text, nullable=False)
#     option2 = db.Column(db.Text, nullable=False)
#     option3 = db.Column(db.Text, nullable=False)
#     option4 = db.Column(db.Text, nullable=False)
#     correct_option = db.Column(db.Integer, nullable=False)  # 1, 2, 3, or 4
#     created_at = db.Column(db.DateTime, default=db.func.current_timestamp()) 

from . import db

class Question(db.Model):
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)  # Renamed from question_statement
    option1 = db.Column(db.Text, nullable=False)
    option2 = db.Column(db.Text, nullable=False)
    option3 = db.Column(db.Text, nullable=False)
    option4 = db.Column(db.Text, nullable=False)
    correct_option = db.Column(db.Integer, nullable=False)  # Keeping as an int
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

