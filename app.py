from flask import Flask, jsonify
from config import Config
from models import db, User, Job
from flask_jwt_extended import JWTManager
from flask_cors import CORS

# Import Blueprints
from routes.auth import auth_bp
from routes.jobs import jobs_bp
from routes.users import users_bp
from routes.admin import admin_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)

    # Initialize Extensions
    db.init_app(app)
    jwt = JWTManager(app)

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(jobs_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(admin_bp)

    # Base route
    @app.route('/')
    def index():
        return jsonify({
            "name": "Worklify API",
            "version": "1.0",
            "status": "Running",
            "message": "Welcome to the Worklify REST API. Please use the /api/ routes."
        })

    # Error Handlers
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"message": "Endpoint not found"}), 404

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"message": "Internal server error"}), 500

    return app

app = create_app()

def seed_database():
    """Seed the database with an admin user and some default jobs for testing"""
    # Create admin user if it doesn't exist
    if not User.query.filter_by(role='admin').first():
        admin = User(name="Admin User", email="admin@worklify.com", role="admin")
        admin.set_password('admin123')
        db.session.add(admin)
        print("[SUCCESS] Created default admin (admin@worklify.com / admin123)")

    # Create dummy jobs if none exist
    if Job.query.count() == 0:
        jobs = [
            Job(title="Senior React Developer", description="Build modern frontend apps using React and Next.js. Remote US.", salary=135000),
            Job(title="Backend Python Engineer", description="Design robust APIs with Flask, SQLAlchemy, and Docker. 100% remote.", salary=125000),
            Job(title="Cloud DevOps Specialist", description="Manage AWS infrastructure, terraform, and CI/CD pipelines.", salary=140000)
        ]
        db.session.bulk_save_objects(jobs)
        print("[SUCCESS] Created 3 sample remote jobs")

    db.session.commit()

# Setup database and seed it on startup
with app.app_context():
    db.create_all()
    seed_database()

if __name__ == '__main__':
    # Run the Flask API Server on a different port to avoid conflicts with your main app
    print("\n[START] Worklify REST API starting on port 5001 (accessible via local network)\n")
    app.run(debug=True, host='0.0.0.0', port=5001)
