from flask import Blueprint, request, jsonify
from models import db, User, Application
from flask_jwt_extended import jwt_required
from utils.decorators import admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
@admin_required()
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users]), 200

@admin_bp.route('/user/<int:user_id>/earnings', methods=['PUT'])
@jwt_required()
@admin_required()
def update_earnings(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    if not data or 'earnings' not in data:
        return jsonify({"message": "Missing earnings field"}), 400
        
    user.earnings = float(data['earnings'])
    db.session.commit()
    
    return jsonify({
        "message": "Earnings updated", 
        "user": user.to_dict()
    }), 200

@admin_bp.route('/applications', methods=['GET'])
@jwt_required()
@admin_required()
def get_applications():
    applications = Application.query.order_by(Application.created_at.desc()).all()
    return jsonify([app.to_dict() for app in applications]), 200

@admin_bp.route('/application/<int:app_id>/status', methods=['PUT'])
@jwt_required()
@admin_required()
def update_application_status(app_id):
    application = Application.query.get_or_404(app_id)
    data = request.get_json()
    
    if not data or 'status' not in data:
        return jsonify({"message": "Missing status field"}), 400
        
    if data['status'] not in ['pending', 'approved', 'rejected']:
        return jsonify({"message": "Invalid status"}), 400
        
    application.status = data['status']
    db.session.commit()
    
    return jsonify({
        "message": f"Application status updated to {application.status}",
        "application": application.to_dict()
    }), 200
