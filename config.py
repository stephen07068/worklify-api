import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Render provides 'postgres://' but SQLAlchemy requires 'postgresql://'
_db_url = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(BASE_DIR, 'database.db')
if _db_url.startswith('postgres://'):
    _db_url = _db_url.replace('postgres://', 'postgresql://', 1)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-key-123'
    SQLALCHEMY_DATABASE_URI = _db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-super-secret-key-456'
    # Tokens expire in 7 days so users stay logged in comfortably
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
    # Email (Gmail SMTP) for password reset
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'worklifyremotejobs@gmail.com')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')  # Gmail App Password
    FRONTEND_URL  = os.environ.get('FRONTEND_URL', 'http://localhost:5000')
