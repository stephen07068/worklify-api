import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta, timezone

from flask import Blueprint, request, jsonify, current_app
from models import db, User
from flask_jwt_extended import create_access_token

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


# ─── helpers ──────────────────────────────────────────────────────────────────

def _send_reset_email(to_email: str, reset_link: str):
    """Send a password-reset email via Gmail SMTP."""
    username = current_app.config['MAIL_USERNAME']
    password = current_app.config['MAIL_PASSWORD']

    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Worklify — Reset your password'
    msg['From']    = f'Worklify <{username}>'
    msg['To']      = to_email

    text_body = (
        f"You requested a password reset for your Worklify account.\n\n"
        f"Click the link below to reset your password (valid for 1 hour):\n\n"
        f"{reset_link}\n\n"
        f"If you did not request this, please ignore this email."
    )
    html_body = f"""
    <div style="font-family:Inter,sans-serif;max-width:540px;margin:0 auto;
                background:#0f172a;color:#e2e8f0;padding:40px;border-radius:16px;">
      <div style="text-align:center;margin-bottom:28px;">
        <span style="font-size:28px;font-weight:800;color:#a78bfa;">⚡ Worklify</span>
      </div>
      <h2 style="margin:0 0 12px;font-size:20px;color:#f8fafc;">Reset your password</h2>
      <p style="color:#94a3b8;line-height:1.6;">
        You requested a password reset for your Worklify account.
        Click the button below — the link expires in <strong>1 hour</strong>.
      </p>
      <div style="text-align:center;margin:32px 0;">
        <a href="{reset_link}"
           style="background:linear-gradient(135deg,#7c3aed,#4f46e5);color:#fff;
                  text-decoration:none;padding:14px 32px;border-radius:10px;
                  font-weight:700;font-size:15px;display:inline-block;">
          Reset Password →
        </a>
      </div>
      <p style="color:#64748b;font-size:13px;">
        If you didn't request this, just ignore this email — your password won't change.
      </p>
      <hr style="border:none;border-top:1px solid #1e293b;margin:28px 0;" />
      <p style="color:#475569;font-size:12px;text-align:center;">
        © 2025 Worklify · worklifyremotejobs@gmail.com
      </p>
    </div>
    """

    msg.attach(MIMEText(text_body, 'plain'))
    msg.attach(MIMEText(html_body, 'html'))

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(username, password)
        server.sendmail(username, to_email, msg.as_string())


# ─── routes ───────────────────────────────────────────────────────────────────

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password') or not data.get('name'):
        return jsonify({"message": "Missing required fields"}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({"message": "Email already registered"}), 400

    new_user = User(
        name=data['name'],
        email=data['email']
    )
    new_user.set_password(data['password'])
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User created successfully", "user": new_user.to_dict()}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"message": "Missing email or password"}), 400

    user = User.query.filter_by(email=data['email']).first()
    if not user or not user.check_password(data['password']):
        return jsonify({"message": "Invalid credentials"}), 401

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role}
    )
    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "user": user.to_dict()
    }), 200


@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """
    Generate a reset token and email a link to the user.
    Always returns 200 to avoid email-enumeration attacks.
    """
    data = request.get_json()
    email = (data or {}).get('email', '').strip().lower()
    if not email:
        return jsonify({"message": "Email is required"}), 400

    user = User.query.filter_by(email=email).first()
    if user:
        token = secrets.token_hex(32)
        user.reset_token = token
        user.reset_token_expires = datetime.now(timezone.utc) + timedelta(hours=1)
        db.session.commit()

        frontend_url = current_app.config['FRONTEND_URL']
        reset_link = f"{frontend_url}/reset-password?token={token}"

        try:
            _send_reset_email(user.email, reset_link)
        except Exception as exc:
            current_app.logger.error(f"[forgot-password] Email send failed: {exc}")
            # Still return 200 so the UI shows success; don't leak the error
    
    return jsonify({
        "message": "If that email is registered, a reset link has been sent."
    }), 200


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """
    Validate the reset token and set the new password.
    """
    data = request.get_json()
    token    = (data or {}).get('token', '').strip()
    password = (data or {}).get('password', '').strip()

    if not token or not password:
        return jsonify({"message": "Token and new password are required"}), 400

    if len(password) < 6:
        return jsonify({"message": "Password must be at least 6 characters"}), 400

    user = User.query.filter_by(reset_token=token).first()
    if not user:
        return jsonify({"message": "Invalid or expired reset link"}), 400

    now = datetime.now(timezone.utc)
    # Make expires timezone-aware if stored as naive UTC
    expires = user.reset_token_expires
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)

    if now > expires:
        return jsonify({"message": "Reset link has expired. Please request a new one."}), 400

    user.set_password(password)
    user.reset_token = None
    user.reset_token_expires = None
    db.session.commit()

    return jsonify({"message": "Password updated successfully. You can now log in."}), 200
