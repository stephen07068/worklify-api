from flask import Blueprint, jsonify
from models import db, User, Job, Application
from flask_jwt_extended import jwt_required, get_jwt_identity

users_bp = Blueprint('users', __name__, url_prefix='/api')

@users_bp.route('/user/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
        
    applications = Application.query.filter_by(user_id=user.id).all()
    
    return jsonify({
        "name": user.name,
        "earnings": f"${user.earnings:,.2f}",
        "applications": [app.to_dict() for app in applications],
        "whatsapp_contact": "https://wa.me/14782338453",
        "email_contact": "worklifyremotejobs@gmail.com"
    }), 200

@users_bp.route('/apply/<int:job_id>', methods=['POST'])
@jwt_required()
def apply_job(job_id):
    user_id = get_jwt_identity()
    job = Job.query.get_or_404(job_id)
    
    # Check if already applied
    existing = Application.query.filter_by(user_id=user_id, job_id=job.id).first()
    if existing:
        return jsonify({"message": "You have already applied for this job"}), 400
        
    application = Application(user_id=user_id, job_id=job.id)
    db.session.add(application)
    db.session.commit()
    
    return jsonify({
        "message": f"Successfully applied for {job.title}",
        "application": application.to_dict()
    }), 201
