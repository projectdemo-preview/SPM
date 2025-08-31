# app.py
from flask import Flask, render_template, url_for, flash, redirect, request, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import pytz
from models import User, Announcement, Resource, Movie, Birthday, Task
from config import Config
import os
import requests
from sqlalchemy import or_
from functools import wraps
import os
from models import db, User, Task, Announcement, Resource, Birthday, Movie, Request
from datetime import datetime
from config import Config
from flask_wtf.csrf import CSRFProtect, generate_csrf
import uuid

# ----------------------------_
# Configuration
# ----------------------------_
app = Flask(__name__)
app.config.from_object(Config)

# Initialize DB and CSRF Protection
db.init_app(app)
csrf = CSRFProtect(app)

with app.app_context():
    db.create_all()
    if not User.query.filter_by(userID='admin').first():
        admin_user = User(
            userID='admin',
            name='Admin User',
            email='admin@example.com',
            is_admin=True
        )
        admin_user.set_password('admin')
        db.session.add(admin_user)
        db.session.commit()

    # Generate public_id for existing tasks
    tasks = Task.query.all()
    for task in tasks:
        if not task.public_id:
            task.public_id = str(uuid.uuid4())
    db.session.commit()

    # Generate public_id for existing users
    users = User.query.all()
    for user in users:
        if not user.public_id:
            user.public_id = str(uuid.uuid4())
    db.session.commit()

    # Generate public_id for existing announcements
    announcements = Announcement.query.all()
    for announcement in announcements:
        if not announcement.public_id:
            announcement.public_id = str(uuid.uuid4())
    db.session.commit()

    # Generate public_id for existing resources
    resources = Resource.query.all()
    for resource in resources:
        if not resource.public_id:
            resource.public_id = str(uuid.uuid4())
    db.session.commit()

    # Generate public_id for existing birthdays
    birthdays = Birthday.query.all()
    for birthday in birthdays:
        if not birthday.public_id:
            birthday.public_id = str(uuid.uuid4())
    db.session.commit()

    # Generate public_id for existing movies
    movies = Movie.query.all()
    for movie in movies:
        if not movie.public_id:
            movie.public_id = str(uuid.uuid4())
    db.session.commit()

    # Generate public_id for existing requests
    requests = Request.query.all()
    for req in requests:
        if not req.public_id:
            req.public_id = str(uuid.uuid4())
    db.session.commit()

# ----------------------------_
# Role-based decorators
# ----------------------------_
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ----------------------------_
# Routes
# ----------------------------_
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
@admin_required
def register():
    if request.method == 'POST':
        userID = request.form['userID']
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        domain = request.form.get('domain')
        position = request.form.get('position')
        duration = request.form.get('duration')

        if User.query.filter((User.userID == userID) | (User.email == email) | (User.name == name)).first():
            flash('User ID, Email, or Name already exists!', 'danger')
            return redirect(url_for('register'))

        new_user = User(
            userID=userID,
            name=name,
            email=email,
            domain=domain,
            position=position,
            duration=duration
        )
        new_user.set_password(password)
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error: {str(e)}", "danger")
            return redirect(url_for('register'))
    return render_template('register.html', csrf_token_value=generate_csrf())

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        userID = request.form['userID']
        password = request.form['password']

        user = User.query.filter_by(userID=userID).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['userID'] = user.userID
            session['is_admin'] = user.is_admin
            session['name'] = user.name

            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('dashboard'))
        else:
            flash('Invalid userID or password!', 'danger')

    return render_template('login.html', csrf_token_value=generate_csrf())

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'info')
    return redirect(url_for('login'))

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    return render_template('forgot_password.html')



# ----------------------------_
# User & Admin Dashboards
# ----------------------------_
@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    tasks = Task.query.filter_by(user_id=user_id).limit(2).all()
    announcements = Announcement.query.filter_by(user_id=user_id).limit(2).all()
    resources = Resource.query.filter_by(user_id=user_id).limit(2).all()
    birthdays = Birthday.query.filter_by(user_id=user_id).all()
    movies = Movie.query.filter_by(user_id=user_id).all()
    requests = Request.query.filter_by(user_id=user_id).limit(8









                                                              ).all()
    return render_template('dashboard.html',
                        tasks=tasks, announcements=announcements, resources=resources,
                        birthdays=birthdays, movies=movies, requests=requests, csrf_token_value=generate_csrf())

@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    users = User.query.limit(5).all()
    tasks = Task.query.limit(5).all()
    announcements = Announcement.query.limit(5).all()
    resources = Resource.query.limit(5).all()
    return render_template('admin_dashboard.html', users=users, tasks=tasks, announcements=announcements, resources=resources, csrf_token_value=generate_csrf())

@app.route('/admin/tasks')
@login_required
@admin_required
def manage_tasks():
    tasks = Task.query.all()
    return render_template('manage_tasks.html', tasks=tasks, csrf_token_value=generate_csrf())

# ----------------------------_
# Task Management
# ----------------------------_
@app.route('/tasks')
@login_required
def tasks():
    user_id = session['user_id']
    tasks = Task.query.filter_by(user_id=user_id).all()
    return render_template('tasks.html', tasks=tasks, csrf_token_value=generate_csrf())

@app.route('/add_task', methods=['GET', 'POST'])
@login_required
def add_task():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        due_date_str = request.form['due_date']
        due_date = datetime.strptime(due_date_str, '%Y-%m-%d') if due_date_str else None
        user_id = session['user_id']
        new_task = Task(title=title, description=description, due_date=due_date, user_id=user_id)
        db.session.add(new_task)
        db.session.commit()
        flash('Task added successfully!', 'success')

        # Check admin using session
        if session.get('is_admin'):
            return redirect(url_for('manage_tasks'))
        else:
            return redirect(url_for('tasks'))

    return render_template('add_task.html', csrf_token_value=generate_csrf())

@app.route('/edit_task/<string:public_id>', methods=['GET', 'POST'])
@login_required
def edit_task(public_id):
    task = Task.query.filter_by(public_id=public_id).first_or_404()
    
    # Debugging: Print request method and public_id
    print(f"Request method: {request.method}, Public ID: {public_id}")

    if request.method == 'POST':
        try:
            task.title = request.form['title']
            task.description = request.form['description']
            due_date_str = request.form['due_date']
            task.due_date = datetime.strptime(due_date_str, '%Y-%m-%d') if due_date_str else None
            db.session.commit()
            
            # Always return JSON for POST requests to simplify debugging AJAX
            return jsonify({
                'success': True,
                'message': 'Task updated successfully!',
                'task': {
                    'public_id': task.public_id,
                    'title': task.title,
                    'description': task.description,
                    'due_date': task.due_date.strftime('%Y-%m-%d') if task.due_date else 'N/A'
                }
            })
        except Exception as e:
            print(f"Error during task update: {e}") # Log the error
            return jsonify({'success': False, 'error': str(e), 'message': 'An internal server error occurred.'}), 500
    
    # For GET requests, render the template (if accessed directly)
    return render_template('edit_task.html', task=task, csrf_token_value=generate_csrf())

@app.route('/delete_task/<string:public_id>', methods=['POST'])
@login_required
def delete_task(public_id):
    task = Task.query.filter_by(public_id=public_id).first_or_404()

    # Optional: prevent non-owners from deleting
    if not session.get('is_admin') and task.user_id != session['user_id']:
        flash('You do not have permission to delete this task.', 'danger')
        return redirect(url_for('tasks'))

    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully!', 'success')

    if session.get('is_admin'):
        return redirect(url_for('manage_tasks'))
    else:
        return redirect(url_for('tasks'))








# ----------------------------_
# Announcement Management (Admin)
# ----------------------------_
@app.route('/admin/announcements')
@login_required
@admin_required
def manage_announcements():
    announcements = Announcement.query.all()
    return render_template('manage_announcements.html', announcements=announcements)

@app.route('/admin/add_announcement', methods=['GET', 'POST'])
@login_required
@admin_required
def add_announcement():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        user_id = session['user_id']
        new_announcement = Announcement(title=title, description=description, user_id=user_id)
        db.session.add(new_announcement)
        db.session.commit()
        flash('Announcement added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('add_announcement.html', csrf_token_value=generate_csrf())

@app.route('/admin/edit_announcement/<string:public_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_announcement(public_id):
    announcement = Announcement.query.filter_by(public_id=public_id).first_or_404()
    if request.method == 'POST':
        announcement.title = request.form['title']
        announcement.description = request.form['description']
        db.session.commit()
        flash('Announcement updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('edit_announcement.html', announcement=announcement, csrf_token_value=generate_csrf())

@app.route('/admin/delete_announcement/<string:public_id>')
@login_required
@admin_required
def delete_announcement(public_id):
    announcement = Announcement.query.filter_by(public_id=public_id).first_or_404()
    db.session.delete(announcement)
    db.session.commit()
    flash('Announcement deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

# ----------------------------_
# Resource Management (Admin)
# ----------------------------_
@app.route('/admin/resources')
@login_required
@admin_required
def manage_resources():
    resources = Resource.query.all()
    return render_template('manage_resources.html', resources=resources)

@app.route('/admin/add_resource', methods=['GET', 'POST'])
@login_required
@admin_required
def add_resource():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        user_id = session['user_id']
        new_resource = Resource(title=title, description=description, user_id=user_id)
        db.session.add(new_resource)
        db.session.commit()
        flash('Resource added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('add_resource.html', csrf_token_value=generate_csrf())

@app.route('/admin/edit_resource/<string:public_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_resource(public_id):
    resource = Resource.query.filter_by(public_id=public_id).first_or_404()
    if request.method == 'POST':
        resource.title = request.form['title']
        resource.description = request.form['description']
        db.session.commit()
        flash('Resource updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('edit_resource.html', resource=resource, csrf_token_value=generate_csrf())

@app.route('/admin/delete_resource/<string:public_id>')
@login_required
@admin_required
def delete_resource(public_id):
    resource = Resource.query.filter_by(public_id=public_id).first_or_404()
    db.session.delete(resource)
    db.session.commit()
    flash('Resource deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

# ----------------------------_
# Announcement Management (User)
# ----------------------------_
@app.route('/announcements')
@login_required
def announcements():
    user_id = session['user_id']
    announcements = Announcement.query.all()
    return render_template('announcements.html', announcements=announcements)

# ----------------------------_
# Resource Management (User)
# ----------------------------_
@app.route('/resources')
@login_required
def resources():
    user_id = session['user_id']
    resources = Resource.query.all()
    return render_template('resources.html', resources=resources)

# ----------------------------_
# User Management (Admin)
# ----------------------------_
@app.route('/admin/users', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_users():
    search_query = request.form.get('search_query')
    view_all = request.args.get('view_all')

    if search_query:
        users = User.query.filter(User.userID.ilike(f'%{search_query}%')).all()
    elif view_all:
        users = User.query.all()
    else:
        users = User.query.limit(10).all()

    return render_template('manage_users.html', users=users, csrf_token_value=generate_csrf())

@app.route('/admin/edit_user/<string:public_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(public_id):
    user = User.query.filter_by(public_id=public_id).first_or_404()
    if request.method == 'POST':
        user.name = request.form['name']
        user.email = request.form['email']
        user.domain = request.form.get('domain')
        user.position = request.form.get('position')
        user.duration = request.form.get('duration')
        user.is_admin = 'is_admin' in request.form
        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('manage_users'))
    return render_template('edit_user.html', user=user, csrf_token_value=generate_csrf())

@app.route('/admin/delete_user/<string:public_id>')
@login_required
@admin_required
def delete_user(public_id):
    user = User.query.filter_by(public_id=public_id).first_or_404()
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('manage_users'))

# ----------------------------_
# User Profile Management
# ----------------------------_
@app.route('/profile')
@login_required
def profile():
    user_id = session['user_id']
    user = User.query.get_or_404(user_id)
    return render_template('profile.html', user=user)

# ----------------------------_
# Birthday Management
# ----------------------------_
@app.route('/birthdays')
@login_required
def birthdays():
    user_id = session['user_id']
    birthdays = Birthday.query.filter_by(user_id=user_id).all()
    return render_template('birthdays.html', birthdays=birthdays)

@app.route('/add_birthday', methods=['GET', 'POST'])
@login_required
def add_birthday():
    if request.method == 'POST':
        name = request.form['name']
        date_of_birth_str = request.form['date_of_birth']
        date_of_birth = datetime.strptime(date_of_birth_str, '%Y-%m-%d').date()
        email = request.form['email']
        subject = request.form.get('subject')
        message = request.form.get('message')
        user_id = session['user_id']
        new_birthday = Birthday(name=name, date_of_birth=date_of_birth, email=email, subject=subject, message=message, user_id=user_id)
        db.session.add(new_birthday)
        db.session.commit()
        flash('Birthday added successfully!', 'success')
        return redirect(url_for('birthdays'))
    return render_template('add_birthday.html', csrf_token_value=generate_csrf())

@app.route('/edit_birthday/<string:public_id>', methods=['GET', 'POST'])
@login_required
def edit_birthday(public_id):
    birthday = Birthday.query.filter_by(public_id=public_id).first_or_404()
    if birthday.user_id != session['user_id']:
        flash('You do not have permission to edit this birthday.', 'danger')
        return redirect(url_for('birthdays'))
    if request.method == 'POST':
        birthday.name = request.form['name']
        date_of_birth_str = request.form['date_of_birth']
        birthday.date_of_birth = datetime.strptime(date_of_birth_str, '%Y-%m-%d').date()
        birthday.email = request.form['email']
        birthday.subject = request.form.get('subject')
        birthday.message = request.form.get('message')
        db.session.commit()
        flash('Birthday updated successfully!', 'success')
        return redirect(url_for('birthdays'))
    return render_template('edit_birthday.html', birthday=birthday, csrf_token_value=generate_csrf())

@app.route('/delete_birthday/<string:public_id>')
@login_required
def delete_birthday(public_id):
    birthday = Birthday.query.filter_by(public_id=public_id).first_or_404()
    if birthday.user_id != session['user_id']:
        flash('You do not have permission to delete this birthday.', 'danger')
        return redirect(url_for('birthdays'))
    db.session.delete(birthday)
    db.session.commit()
    flash('Birthday deleted successfully!', 'success')
    return redirect(url_for('birthdays'))

# ----------------------------_
# Movie Management
# ----------------------------_
@app.route('/movies')
@login_required
def movies():
    user_id = session['user_id']
    movies = Movie.query.filter_by(user_id=user_id).all()
    return render_template('movies.html', movies=movies)

@app.route('/add_movie', methods=['GET', 'POST'])
@login_required
def add_movie():
    if request.method == 'POST':
        movie_name = request.form['movie_name']
        release_date_str = request.form['release_date']
        release_date = datetime.strptime(release_date_str, '%Y-%m-%d').date()
        user_id = session['user_id']
        new_movie = Movie(movie_name=movie_name, release_date=release_date, user_id=user_id)
        db.session.add(new_movie)
        db.session.commit()
        flash('Movie added successfully!', 'success')
        return redirect(url_for('movies'))
    return render_template('add_movie.html', csrf_token_value=generate_csrf())

@app.route('/edit_movie/<string:public_id>', methods=['GET', 'POST'])
@login_required
def edit_movie(public_id):
    movie = Movie.query.filter_by(public_id=public_id).first_or_404()
    if movie.user_id != session['user_id']:
        flash('You do not have permission to edit this movie.', 'danger')
        return redirect(url_for('movies'))
    if request.method == 'POST':
        movie.movie_name = request.form['movie_name']
        release_date_str = request.form['release_date']
        movie.release_date = datetime.strptime(release_date_str, '%Y-%m-%d').date()
        db.session.commit()
        flash('Movie updated successfully!', 'success')
        return redirect(url_for('movies'))
    return render_template('edit_movie.html', movie=movie, csrf_token_value=generate_csrf())

@app.route('/delete_movie/<string:public_id>')
@login_required
def delete_movie(public_id):
    movie = Movie.query.filter_by(public_id=public_id).first_or_404()
    if movie.user_id != session['user_id']:
        flash('You do not have permission to delete this movie.', 'danger')
        return redirect(url_for('movies'))
    db.session.delete(movie)
    db.session.commit()
    flash('Movie deleted successfully!', 'success')
    return redirect(url_for('movies'))

@app.route('/admin/add', methods=['POST'])
@login_required
@admin_required
def admin_add():
    item_type = request.form.get('item_type')
    title = request.form.get('title')
    description = request.form.get('description')
    user_public_id = request.form.get('user_id') # Get the public_id string

    user = User.query.filter_by(public_id=user_public_id).first_or_404() # Fetch the user object
    user_id = user.id # Get the integer user_id

    if not all([item_type, title, user_public_id]): # Check user_public_id instead of user_id
        flash('Missing required fields!', 'danger')
        return redirect(url_for('admin_dashboard'))

    if item_type == 'task':
        due_date_str = request.form.get('due_date')
        due_date = datetime.strptime(due_date_str, '%Y-%m-%d') if due_date_str else None
        new_item = Task(title=title, description=description, due_date=due_date, user_id=user_id) # Use integer user_id
    elif item_type == 'announcement':
        new_item = Announcement(title=title, description=description, user_id=user_id) # Use integer user_id
    elif item_type == 'resource':
        new_item = Resource(title=title, description=description, user_id=user_id) # Use integer user_id
    else:
        flash('Invalid item type!', 'danger')
        return redirect(url_for('admin_dashboard'))

    db.session.add(new_item)
    db.session.commit()
    flash(f'{item_type.capitalize()} added successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/my_requests')
@login_required
def my_requests():
    user_id = session['user_id']
    requests = Request.query.filter_by(user_id=user_id).all()
    return render_template('my_requests.html', requests=requests)

# -----------------------------
# Team Management (Admin)
# -----------------------------
""" 
@app.route('/admin/teams')
@login_required
@admin_required
def manage_teams():
    teams = Team.query.all()
    return render_template('manage_teams.html', teams=teams)

@app.route('/admin/add_team', methods=['GET', 'POST'])
@login_required
@admin_required
def add_team():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form.get('description')
        admin_id = current_user.id # The admin creating the team

        new_team = Team(name=name, description=description, admin_id=admin_id)
        db.session.add(new_team)
        db.session.commit()
        flash('Team added successfully!', 'success')
        return redirect(url_for('manage_teams'))
    return render_template('add_team.html')

@app.route('/admin/edit_team/<int:team_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_team(team_id):
    team = Team.query.get_or_404(team_id)
    if request.method == 'POST':
        team.name = request.form['name']
        team.description = request.form.get('description')
        db.session.commit()
        flash('Team updated successfully!', 'success')
        return redirect(url_for('manage_teams'))
    return render_template('edit_team.html', team=team)

@app.route('/admin/delete_team/<int:team_id>', methods=['POST'])
@login_required
@admin_required
def delete_team(team_id):
    team = Team.query.get_or_404(team_id)
    db.session.delete(team)
    db.session.commit()
    flash('Team deleted successfully!', 'success')
    return redirect(url_for('manage_teams'))

@app.route('/admin/teams/<int:team_id>/members', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_team_members(team_id):
    team = Team.query.get_or_404(team_id)
    all_users = User.query.all()
    
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        action = request.form.get('action') # 'add' or 'remove'
        
        user = User.query.get_or_404(user_id)
        
        if action == 'add':
            user.team_id = team.id
            flash(f'{user.name} added to {team.name}!', 'success')
        elif action == 'remove':
            user.team_id = None # Remove from team
            flash(f'{user.name} removed from {team.name}!', 'success')
        
        db.session.commit()
        return redirect(url_for('manage_team_members', team_id=team.id))
        
    return render_template('manage_team_members.html', team=team, all_users=all_users)
    
    """

# -----------------------------
# Request Management
# -----------------------------
@app.route('/add_request', methods=['POST'])
@login_required
def add_request():
    request_type = request.form.get('request_type')
    title = request.form.get('title')
    description = request.form.get('description')
    user_id = session['user_id']

    if not all([request_type, title]):
        flash('Missing required fields!', 'danger')
        return redirect(url_for('dashboard'))

    new_request = Request(
        user_id=user_id,
        request_type=request_type,
        title=title,
        description=description
    )
    db.session.add(new_request)
    db.session.commit()
    flash('Your request has been submitted and is pending approval.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/admin/requests')
@login_required
@admin_required
def manage_requests():
    requests = Request.query.filter_by(status='Pending').all()
    return render_template('admin_requests.html', requests=requests, csrf_token_value=generate_csrf())

@app.route('/admin/approve_request/<string:public_id>', methods=['POST'])
@login_required
@admin_required
def approve_request(public_id):
    req = Request.query.filter_by(public_id=public_id).first_or_404()
    admin_message = request.form.get('admin_message')
    if req.request_type == 'Task':
        new_item = Task(title=req.title, description=req.description, user_id=req.user_id)
    elif req.request_type == 'Announcement':
        new_item = Announcement(title=req.title, description=req.description, user_id=req.user_id)
    elif req.request_type == 'Resource':
        new_item = Resource(title=req.title, description=req.description, user_id=req.user_id)
    else:
        flash('Invalid request type!', 'danger')
        return redirect(url_for('manage_requests'))

    db.session.add(new_item)
    req.status = 'Approved'
    req.admin_message = admin_message
    db.session.commit()
    flash('Request approved and item added.', 'success')
    return redirect(url_for('manage_requests'))

@app.route('/admin/reject_request/<string:public_id>', methods=['POST'])
@login_required
@admin_required
def reject_request(public_id):
    req = Request.query.filter_by(public_id=public_id).first_or_404()
    admin_message = request.form.get('admin_message')
    req.status = 'Rejected'
    req.admin_message = admin_message
    db.session.commit()
    flash('Request rejected.', 'success')
    return redirect(url_for('manage_requests'))

@app.after_request
def add_header(response):
    """
    Add headers to prevent caching.
    """
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


# -----------------------------
# Run
# -----------------------------




@app.route('/admin/add_item/<string:public_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_item(public_id):
    user = User.query.filter_by(public_id=public_id).first_or_404()
    if request.method == 'POST':
        item_type = request.form.get('item_type')
        title = request.form.get('title')
        description = request.form.get('description')

        if not all([item_type, title]):
            flash('Missing required fields!', 'danger')
            return redirect(url_for('admin_add_item', user_id=user_id))

        if item_type == 'task':
            due_date_str = request.form.get('due_date')
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d') if due_date_str else None
            new_item = Task(title=title, description=description, due_date=due_date, user_id=user_id)
        elif item_type == 'announcement':
            new_item = Announcement(title=title, description=description, user_id=user_id)
        elif item_type == 'resource':
            new_item = Resource(title=title, description=description, user_id=user_id)
        else:
            flash('Invalid item type!', 'danger')
            return redirect(url_for('admin_add_item', user_id=user_id))

        db.session.add(new_item)
        db.session.commit()
        flash(f'{item_type.capitalize()} added successfully for {user.name}!', 'success')
        return redirect(url_for('manage_users'))
    return render_template('admin_add_item.html', user=user, csrf_token_value=generate_csrf())

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")