from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from models import db
from models.subject import Subject
from models.chapter import Chapter
from models.quiz import Quiz
from models.question import Question
from models.score import Score
from models.user import User
from datetime import datetime

user = Blueprint('user', __name__, url_prefix='/user')

@user.route('/')
@login_required
def dashboard():
    user_id = current_user.id  

    # Get user's quiz attempts
    scores = Score.query.filter_by(user_id=user_id).order_by(Score.time_stamp_of_attempt.desc()).all()

    # Calculate user stats
    completed_quizzes = len(scores)
    average_score = sum([s.total_scored for s in scores]) / completed_quizzes if completed_quizzes > 0 else 0

    # Create a stats dictionary
    stats = {
        "completed": completed_quizzes,
        "average_score": round(average_score, 2)
    }

    # Get all subjects for navigation
    subjects = Subject.query.all()

    return render_template('user/dashboard.html', 
                           scores=scores,
                           subjects=subjects,
                           stats=stats,
                           current_user=current_user)


@user.route('/history')
@login_required
def history():
    """View past quiz attempts"""
    user_id = current_user.id
    scores = Score.query.filter_by(user_id=user_id).order_by(Score.time_stamp_of_attempt.desc()).all()

    return render_template('user/history.html', scores=scores)


@user.route('/subjects')
@login_required
def subjects():
    subjects = Subject.query.all()
    return render_template('user/subjects.html', subjects=subjects)

@user.route('/subjects/<int:subject_id>/chapters')
@login_required
def chapters(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    chapters = Chapter.query.filter_by(subject_id=subject_id).all()
    
    return render_template('user/chapters.html', 
                           subject=subject, chapters=chapters)

@user.route('/chapters/<int:chapter_id>/quizzes')
@login_required
def quizzes(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
    
    return render_template('user/quizzes.html',
                           chapter=chapter, quizzes=quizzes)

@user.route('/quizzes/<int:quiz_id>/take')
@login_required
def take_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    
    if not questions:
        flash('This quiz has no questions yet!')
        return redirect(url_for('user.quizzes', chapter_id=quiz.chapter_id))
    
    # Convert duration to seconds if available
    duration_seconds = None
    if quiz.time_duration:
        try:
            hours, minutes = map(int, quiz.time_duration.split(':'))
            duration_seconds = (hours * 60 * 60) + (minutes * 60)
        except (ValueError, AttributeError):
            duration_seconds = None
    
    return render_template('user/take_quiz.html',
                           quiz=quiz, 
                           questions=questions,
                           duration_seconds=duration_seconds)

@user.route('/quizzes/<int:quiz_id>/submit', methods=['POST'])
@login_required
def submit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    user_id = current_user.id  

    # Get all questions for this quiz
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    total_questions = len(questions)
    
    if not total_questions:
        flash('This quiz has no questions!')
        return redirect(url_for('user.quizzes', chapter_id=quiz.chapter_id))
    
    # Calculate score
    score = 0
    for question in questions:
        user_answer = request.form.get(f'question_{question.id}')
        if user_answer and int(user_answer) == question.correct_option:
            score += 1
    
    # Record time taken if provided
    time_taken = request.form.get('time_taken')
    if time_taken:
        try:
            time_taken = int(time_taken)
        except (ValueError, TypeError):
            time_taken = None
    
    # Save the score
    new_score = Score(
        quiz_id=quiz_id,
        user_id=user_id,
        total_scored=score,
        total_questions=total_questions,
        time_taken=time_taken
    )
    
    db.session.add(new_score)
    db.session.commit()
    
    flash(f'Quiz submitted! Your score: {score}/{total_questions}')
    return redirect(url_for('user.view_score', score_id=new_score.id))

@user.route('/scores/<int:score_id>')
@login_required
def view_score(score_id):
    user_id = current_user.id  
    score = Score.query.get_or_404(score_id)
    
    # Make sure user can only see their own scores
    if score.user_id != user_id:
        flash('You can only view your own scores!')
        return redirect(url_for('user.dashboard'))
    
    # Get quiz and questions for reviewing
    quiz = Quiz.query.get(score.quiz_id)
    questions = Question.query.filter_by(quiz_id=score.quiz_id).all()
    
    return render_template('user/score.html',
                           score=score,
                           quiz=quiz,
                           questions=questions)
