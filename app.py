# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
import os

# -----------------------------
# Configuration
# -----------------------------
app = Flask(__name__)

# Secret key for session/flash
app.secret_key = os.environ.get('SECRET_KEY', 'supersecretkey')

# Use SQLite for free plan
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydb.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize DB
db = SQLAlchemy(app)

with app.app_context():
    db.create_all()

# -----------------------------
# Models (Example Structure)
# -----------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userID = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    is_admin = db.Column(db.Boolean, default=False)
    domain = db.Column(db.String(100))
    position = db.Column(db.String(50))
    duration = db.Column(db.String(50))

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    due_date = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Birthday(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    date_of_birth = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class MovieAlert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    movie_name = db.Column(db.String(100))
    release_date = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# -----------------------------
# Create DB and default admin
# -----------------------------
with app.app_context():
    db.create_all()
    if not User.query.filter_by(userID='admin').first():
        admin_user = User(
            userID='admin',
            name='Admin User',
            email='admin@example.com',
            password='admin',  # Consider hashing for production
            is_admin=True
        )
        db.session.add(admin_user)
        db.session.commit()

# -----------------------------
# Role-based decorators
# -----------------------------
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

# -----------------------------
# Routes
# -----------------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        userID = request.form['userID']
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        domain = request.form.get('domain')
        position = request.form.get('position')
        duration = request.form.get('duration')

        if User.query.filter((User.userID == userID) | (User.email == email)).first():
            flash('User ID or Email already exists!', 'danger')
            return redirect(url_for('register'))

        new_user = User(
            userID=userID,
            name=name,
            email=email,
            password=password,  # Consider hashing
            domain=domain,
            position=position,
            duration=duration
        )
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error: {str(e)}", "danger")
            return redirect(url_for('register'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        userID = request.form['userID']
        password = request.form['password']

        user = User.query.filter_by(userID=userID).first()
        if user and user.password == password:
            session['user_id'] = user.id
            session['userID'] = user.userID
            session['is_admin'] = user.is_admin

            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('dashboard'))
        else:
            flash('Invalid userID or password!', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'info')
    return redirect(url_for('login'))

# -----------------------------
# User & Admin Dashboards
# -----------------------------
@app.route('/dashboard')
@login_required
def dashboard():
    try:
        user_id = session['user_id']
        tasks = Task.query.filter_by(user_id=user_id).all()
        announcements = Announcement.query.filter_by(user_id=user_id).all()
        resources = Resource.query.filter_by(user_id=user_id).all()
        birthdays = Birthday.query.filter_by(user_id=user_id).all()
        movies = MovieAlert.query.filter_by(user_id=user_id).all()
        return render_template('dashboard.html',
                            tasks=tasks, announcements=announcements, resources=resources,
                            birthdays=birthdays, movies=movies)
    except Exception as e:
        return f"Error in dashboard: {e}"


@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    users = User.query.filter_by(is_admin=False).all()
    return render_template('admin_dashboard.html', users=users)

# Additional admin/user routes remain the same as your original code
# -----------------------------
# Run
# -----------------------------

if __name__ == '__main__':
    app.run(debug=False)
