# from flask import Blueprint, render_template, redirect, url_for, request, flash
# from flask_login import login_user, logout_user, login_required
# from werkzeug.security import generate_password_hash, check_password_hash
# from models import db
# from models.user import User
# from datetime import datetime

# auth = Blueprint('auth', __name__)

# @auth.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         email = request.form.get('email')
#         password = request.form.get('password')
        
#         user = User.query.filter_by(email=email).first()
        
#         if not user or not user.check_password(password):
#             flash('Invalid login details. Please try again.')
#             return redirect(url_for('auth.login'))

#         # Log in the user using Flask-Login
#         login_user(user)

#         if user.is_admin:
#             return redirect(url_for('admin.dashboard'))
#         else:
#             return redirect(url_for('user.dashboard'))
    
#     return render_template('auth/login.html')

# @auth.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         email = request.form.get('email')
#         password = request.form.get('password')
#         full_name = request.form.get('full_name')
#         qualification = request.form.get('qualification')
#         dob_str = request.form.get('dob')

#         # Check if user already exists
#         user = User.query.filter_by(email=email).first()
#         if user:
#             flash('Email address already exists')
#             return redirect(url_for('auth.register'))
        
#         # Parse date of birth
#         try:
#             dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
#         except (ValueError, TypeError):
#             dob = None
        
#         # Create new user
#         new_user = User(
#             email=email,
#             full_name=full_name,
#             qualification=qualification,
#             dob=dob,
#             is_admin=False
#         )
#         new_user.set_password(password)
        
#         # Add user to database
#         db.session.add(new_user)
#         db.session.commit()
        
#         flash('Registration successful! Please log in.')
#         return redirect(url_for('auth.login'))
    
#     return render_template('auth/register.html')

# @auth.route('/logout')
# @login_required
# def logout():
#     logout_user()  # Properly log out the user
#     return redirect(url_for('auth.login'))

from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db
from models.user import User
from datetime import datetime

auth = Blueprint('auth', __name__)

# 🔹 USER LOGIN
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash('Invalid login details. Please try again.', 'danger')
            return redirect(url_for('auth.login'))

        # Log in the user using Flask-Login
        login_user(user)

        # Redirect based on user role
        if user.is_admin:
            return redirect(url_for('admin.dashboard'))  # Redirect admin to admin dashboard
        else:
            return redirect(url_for('user.dashboard'))  # Redirect normal users to their dashboard

    return render_template('auth/login.html')

# 🔹 ADMIN LOGIN (Separate Route)
@auth.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        admin = User.query.filter_by(email=email, is_admin=True).first()
        if not admin or not admin.check_password(password):
            flash('Invalid admin credentials!', 'danger')
            return redirect(url_for('auth.admin_login'))

        # ✅ Set session variables
        login_user(admin)
        session['user_id'] = admin.id
        session['is_admin'] = True  # Ensure this is set

        print("Session Data after login:", session)  # ✅ Debugging step

        flash('Admin login successful!', 'success')
        return redirect(url_for('admin.dashboard'))  # Redirect correctly

    return render_template('admin/admin_login.html')

# 🔹 USER REGISTRATION
@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        qualification = request.form.get('qualification')
        dob_str = request.form.get('dob')

        # Check if user already exists
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email address already exists', 'danger')
            return redirect(url_for('auth.register'))

        # Parse date of birth
        try:
            dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            dob = None

        # Create new user (default is not admin)
        new_user = User(
            email=email,
            full_name=full_name,
            qualification=qualification,
            dob=dob,
            is_admin=False  # Ensure new users are NOT admins
        )
        new_user.set_password(password)

        # Add user to database
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/dashboard.html')

# 🔹 LOGOUT FUNCTION (Clears Admin Session If Needed)
@auth.route('/logout')
@login_required
def logout():
    logout_user()  # Properly log out the user
    session.pop('is_admin', None)  # Remove admin session if present
    flash("You have been logged out.", "info")
    return redirect(url_for('auth.login'))
