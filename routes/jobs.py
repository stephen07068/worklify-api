from flask import Blueprint, request, jsonify
from models import db, Job
from flask_jwt_extended import jwt_required
from utils.decorators import admin_required
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app

jobs_bp = Blueprint('jobs', __name__, url_prefix='/api/jobs')

@jobs_bp.route('', methods=['GET'])
def get_jobs():
    jobs = Job.query.order_by(Job.created_at.desc()).all()
    return jsonify([job.to_dict() for job in jobs]), 200

@jobs_bp.route('/<int:job_id>', methods=['GET'])
def get_job(job_id):
    job = Job.query.get_or_404(job_id)
    return jsonify(job.to_dict()), 200

@jobs_bp.route('', methods=['POST'])
@jwt_required()
@admin_required()
def create_job():
    data = request.get_json()
    if not data or 'title' not in data or 'description' not in data or 'salary' not in data:
        return jsonify({"message": "Missing required fields: title, description, salary"}), 400
    
    new_job = Job(
        title=data['title'],
        description=data['description'],
        salary=float(data['salary'])
    )
    db.session.add(new_job)
    db.session.commit()
    return jsonify({"message": "Job created", "job": new_job.to_dict()}), 201

@jobs_bp.route('/<int:job_id>', methods=['PUT'])
@jwt_required()
@admin_required()
def update_job(job_id):
    job = Job.query.get_or_404(job_id)
    data = request.get_json()
    
    if 'title' in data:
        job.title = data['title']
    if 'description' in data:
        job.description = data['description']
    if 'salary' in data:
        job.salary = float(data['salary'])
        
    db.session.commit()
    return jsonify({"message": "Job updated", "job": job.to_dict()}), 200

@jobs_bp.route('/<int:job_id>', methods=['DELETE'])
@jwt_required()
@admin_required()
def delete_job(job_id):
    job = Job.query.get_or_404(job_id)
    db.session.delete(job)
    db.session.commit()
    return jsonify({"message": "Job deleted"}), 200

@jobs_bp.route('/application-letter', methods=['POST'])
@jwt_required()
def submit_application_letter():
    data = request.get_json()
    if not data or 'name' not in data or 'email' not in data or 'job_title' not in data or 'letter' not in data:
        return jsonify({"message": "Missing required fields"}), 400

    username = current_app.config.get('MAIL_USERNAME', 'worklifyremotejobs@gmail.com')
    password = current_app.config.get('MAIL_PASSWORD', '')

    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"New Application Letter from {data['name']}"
        msg['From']    = f"Worklify Platform <{username}>"
        msg['To']      = username  # Send to own admin address

        text_body = f"Name: {data['name']}\nEmail: {data['email']}\nTarget Job: {data['job_title']}\n\nLetter:\n{data['letter']}"
        msg.attach(MIMEText(text_body, 'plain'))

        # Only send if password isn't empty, otherwise it's local test mode
        if password:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(username, password)
                server.sendmail(username, username, msg.as_string())
    except Exception as exc:
        current_app.logger.error(f"[application-letter] Email send failed: {exc}")
        # Return standard 500 if email actually fails to send
        return jsonify({"message": "Failed to send email. Ensure API email variables are configured."}), 500

    return jsonify({"message": "Application letter sent successfully."}), 200

