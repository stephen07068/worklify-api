import os
import sys
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Railway provides 'postgresql://' directly; Render used to give 'postgres://'
# Both are normalised to 'postgresql://' for SQLAlchemy compatibility.
_db_url = os.environ.get('DATABASE_URL') or os.environ.get('DATABASE_PRIVATE_URL')
if not _db_url:
    print(
        "WARNING: No DATABASE_URL environment variable found! "
        "Falling back to local SQLite (database.db). "
        "Data will be LOST on redeploy. "
        "Set DATABASE_URL in your Railway environment variables.",
        file=sys.stderr,
    )
    _db_url = 'sqlite:///' + os.path.join(BASE_DIR, 'database.db')
elif _db_url.startswith('postgres://'):
    # Old Render-style URL — normalise for SQLAlchemy
    _db_url = _db_url.replace('postgres://', 'postgresql://', 1)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-key-123'
    SQLALCHEMY_DATABASE_URI = _db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-super-secret-key-456'
    # Tokens expire in 7 days so users stay logged in comfortably
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
    # Email (Gmail SMTP) for password reset / application letters
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'worklifyremotejobs@gmail.com')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')  # Gmail App Password
    FRONTEND_URL  = os.environ.get('FRONTEND_URL', 'http://localhost:5000')

