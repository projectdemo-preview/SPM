# config.py
import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:python@localhost:5432/PMS'
    SECRET_KEY = os.urandom(24)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Your email configuration
    EMAIL_USER = 'onlyresources0@gmail.com'
    EMAIL_PASS = 'blfl sfjo whtb olkp'  # Or use app-specific password for Gmail
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_PORT = 465  # Use 465 for SSL if needed
    EMAIL_USE_TLS = True
