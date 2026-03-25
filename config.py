import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-key-123'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(BASE_DIR, 'database.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-super-secret-key-456'
    # Tokens expire in 1 day for convenience during testing
    JWT_ACCESS_TOKEN_EXPIRES = 86400
    # Email (Gmail SMTP) for password reset
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'worklifyremotejobs@gmail.com')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')  # Gmail App Password
    FRONTEND_URL  = os.environ.get('FRONTEND_URL', 'http://localhost:5000')
