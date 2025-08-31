# config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Secret key for session management and CSRF protection
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Email configuration
    EMAIL_USER = os.environ.get('EMAIL_USER')
    EMAIL_PASS = os.environ.get('EMAIL_PASS')
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_PORT = 465
    EMAIL_USE_TLS = True