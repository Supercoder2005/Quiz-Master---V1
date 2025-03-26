from flask import Blueprint, render_template, redirect, url_for, request, flash, session, jsonify
from models import db
from models.subject import Subject
from models.chapter import Chapter
from models.quiz import Quiz
from models.question import Question
from models.user import User
from models.score import Score
from datetime import datetime
import functools

admin = Blueprint('admin', __name__, url_prefix='/admin')

# Admin authentication decorator
def admin_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or not session.get('is_admin'):
            flash('You need to be an admin to access this page.')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin.route('/')
@admin_required
def dashboard():
    # Count statistics for dashboard
    subjects_count = Subject.query.count()
    chapters_count = Chapter.query.count()
    quizzes_count = Quiz.query.count()
    users_count = User.query.filter_by(is_admin=False).count()
    
    return render_template('admin/dashboard.html', 
                           subjects_count=subjects_count,
                           chapters_count=chapters_count,
                           quizzes_count=quizzes_count,
                           users_count=users_count)

# Subject CRUD operations
@admin.route('/subjects')
@admin_required
def subjects():
    subjects = Subject.query.all()
    return render_template('admin/subjects.html', subjects=subjects)

@admin.route('/subjects/create', methods=['GET', 'POST'])
@admin_required
def create_subject():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        if not name:
            flash('Subject name is required!')
            return redirect(url_for('admin.create_subject'))
        
        subject = Subject(name=name, description=description)
        db.session.add(subject)
        db.session.commit()
        
        flash('Subject created successfully!')
        return redirect(url_for('admin.subjects'))
    
    return render_template('admin/create_subject.html')

@admin.route('/subjects/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_subject(id):
    subject = Subject.query.get_or_404(id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        if not name:
            flash('Subject name is required!')
            return redirect(url_for('admin.edit_subject', id=id))
        
        subject.name = name
        subject.description = description
        db.session.commit()
        
        flash('Subject updated successfully!')
        return redirect(url_for('admin.subjects'))
    
    return render_template('admin/edit_subject.html', subject=subject)

@admin.route('/subjects/<int:id>/delete', methods=['POST'])
@admin_required
def delete_subject(id):
    subject = Subject.query.get_or_404(id)
    db.session.delete(subject)
    db.session.commit()
    
    flash('Subject deleted successfully!')
    return redirect(url_for('admin.subjects'))

# Chapter CRUD operations
@admin.route('/subjects/<int:subject_id>/chapters')
@admin_required
def chapters(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    chapters = Chapter.query.filter_by(subject_id=subject_id).all()
    
    return render_template('admin/chapters.html', 
                           subject=subject, chapters=chapters)

@admin.route('/subjects/<int:subject_id>/chapters/create', methods=['GET', 'POST'])
@admin_required
def create_chapter(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        if not name:
            flash('Chapter name is required!')
            return redirect(url_for('admin.create_chapter', subject_id=subject_id))
        
        chapter = Chapter(subject_id=subject_id, name=name, description=description)
        db.session.add(chapter)
        db.session.commit()
        
        flash('Chapter created successfully!')
        return redirect(url_for('admin.chapters', subject_id=subject_id))
    
    return render_template('admin/create_chapter.html', subject=subject)

@admin.route('/chapters/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_chapter(id):
    chapter = Chapter.query.get_or_404(id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        if not name:
            flash('Chapter name is required!')
            return redirect(url_for('admin.edit_chapter', id=id))
        
        chapter.name = name
        chapter.description = description
        db.session.commit()
        
        flash('Chapter updated successfully!')
        return redirect(url_for('admin.chapters', subject_id=chapter.subject_id))
    
    return render_template('admin/edit_chapter.html', chapter=chapter)

@admin.route('/chapters/<int:id>/delete', methods=['POST'])
@admin_required
def delete_chapter(id):
    chapter = Chapter.query.get_or_404(id)
    subject_id = chapter.subject_id
    
    db.session.delete(chapter)
    db.session.commit()
    
    flash('Chapter deleted successfully!')
    return redirect(url_for('admin.chapters', subject_id=subject_id))

# Quiz CRUD operations
@admin.route('/chapters/<int:chapter_id>/quizzes')
@admin_required
def quizzes(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
    
    return render_template('admin/quizzes.html',
                           chapter=chapter, quizzes=quizzes)

@admin.route('/chapters/<int:chapter_id>/quizzes/create', methods=['GET', 'POST'])
@admin_required
def create_quiz(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        date_of_quiz_str = request.form.get('date_of_quiz')
        time_duration = request.form.get('time_duration')
        remarks = request.form.get('remarks')
        
        if not title:
            flash('Quiz title is required!')
            return redirect(url_for('admin.create_quiz', chapter_id=chapter_id))
        
        # Parse date
        try:
            date_of_quiz = datetime.strptime(date_of_quiz_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            date_of_quiz = None
        
        quiz = Quiz(
            chapter_id=chapter_id,
            title=title,
            description=description,
            date_of_quiz=date_of_quiz,
            time_duration=time_duration,
            remarks=remarks
        )
        
        db.session.add(quiz)
        db.session.commit()
        
        flash('Quiz created successfully!')
        return redirect(url_for('admin.quizzes', chapter_id=chapter_id))
    
    return render_template('admin/create_quiz.html', chapter=chapter)

@admin.route('/quizzes/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_quiz(id):
    quiz = Quiz.query.get_or_404(id)
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        date_of_quiz_str = request.form.get('date_of_quiz')
        time_duration = request.form.get('time_duration')
        remarks = request.form.get('remarks')
        
        if not title:
            flash('Quiz title is required!')
            return redirect(url_for('admin.edit_quiz', id=id))
        
        # Parse date
        try:
            date_of_quiz = datetime.strptime(date_of_quiz_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            date_of_quiz = None
        
        quiz.title = title
        quiz.description = description
        quiz.date_of_quiz = date_of_quiz
        quiz.time_duration = time_duration
        quiz.remarks = remarks
        
        db.session.commit()
        
        flash('Quiz updated successfully!')
        return redirect(url_for('admin.quizzes', chapter_id=quiz.chapter_id))
    
    return render_template('admin/edit_quiz.html', quiz=quiz)

@admin.route('/quizzes/<int:id>/delete', methods=['POST'])
@admin_required
def delete_quiz(id):
    quiz = Quiz.query.get_or_404(id)
    chapter_id = quiz.chapter_id
    
    db.session.delete(quiz)
    db.session.commit()
    
    flash('Quiz deleted successfully!')
    return redirect(url_for('admin.quizzes', chapter_id=chapter_id))

# Question CRUD operations
@admin.route('/quizzes/<int:quiz_id>/questions')
@admin_required
def questions(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    
    return render_template('admin/questions.html',
                           quiz=quiz, questions=questions)

@admin.route('/quizzes/<int:quiz_id>/questions/create', methods=['GET', 'POST'])
@admin_required
def create_question(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    
    if request.method == 'POST':
        question_statement = request.form.get('question_statement')
        option1 = request.form.get('option1')
        option2 = request.form.get('option2')
        option3 = request.form.get('option3')
        option4 = request.form.get('option4')
        correct_option = request.form.get('correct_option')
        
        if not question_statement or not option1 or not option2 or not option3 or not option4 or not correct_option:
            flash('All fields are required!')
            return redirect(url_for('admin.create_question', quiz_id=quiz_id))
        
        question = Question(
            quiz_id=quiz_id,
            question_statement=question_statement,
            option1=option1,
            option2=option2,
            option3=option3,
            option4=option4,
            correct_option=int(correct_option)
        )
        
        db.session.add(question)
        db.session.commit()
        
        flash('Question created successfully!')
        return redirect(url_for('admin.questions', quiz_id=quiz_id))
    
    return render_template('admin/create_question.html', quiz=quiz)

@admin.route('/questions/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_question(id):
    question = Question.query.get_or_404(id)
    
    if request.method == 'POST':
        question_statement = request.form.get('question_statement')
        option1 = request.form.get('option1')
        option2 = request.form.get('option2')
        option3 = request.form.get('option3')
        option4 = request.form.get('option4')
        correct_option = request.form.get('correct_option')
        
        if not question_statement or not option1 or not option2 or not option3 or not option4 or not correct_option:
            flash('All fields are required!')
            return redirect(url_for('admin.edit_question', id=id))
        
        question.question_statement = question_statement
        question.option1 = option1
        question.option2 = option2
        question.option3 = option3
        question.option4 = option4
        question.correct_option = int(correct_option)
        
        db.session.commit()
        
        flash('Question updated successfully!')
        return redirect(url_for('admin.questions', quiz_id=question.quiz_id))
    
    return render_template('admin/edit_question.html', question=question)

@admin.route('/questions/<int:id>/delete', methods=['POST'])
@admin_required
def delete_question(id):
    question = Question.query.get_or_404(id)
    quiz_id = question.quiz_id
    
    db.session.delete(question)
    db.session.commit()
    
    flash('Question deleted successfully!')
    return redirect(url_for('admin.questions', quiz_id=quiz_id))

# User management
@admin.route('/users')
@admin_required
def users():
    users = User.query.filter_by(is_admin=False).all()
    return render_template('admin/users.html', users=users)

# Search functionality
@admin.route('/search', methods=['GET'])
@admin_required
def search():
    query = request.args.get('query', '')
    
    if not query:
        return render_template('admin/search.html', results=None)
    
    # Search in users (non-admin)
    users = User.query.filter(
        User.is_admin == False,
        (User.email.like(f'%{query}%') | User.full_name.like(f'%{query}%'))
    ).all()
    
    # Search in subjects
    subjects = Subject.query.filter(
        Subject.name.like(f'%{query}%') | Subject.description.like(f'%{query}%')
    ).all()
    
    # Search in quizzes
    quizzes = Quiz.query.filter(
        Quiz.title.like(f'%{query}%') | Quiz.description.like(f'%{query}%')
    ).all()
    
    return render_template('admin/search.html', results={
        'users': users,
        'subjects': subjects,
        'quizzes': quizzes
    })