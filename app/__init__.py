from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
import os

db = SQLAlchemy()
login_manager = LoginManager()

def create_app(config_class=Config):
    app = Flask(__name__, template_folder='../templates') 
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Create necessary directories
    os.makedirs(os.path.join(app.instance_path, '..', 'database'), exist_ok=True)
    os.makedirs(os.path.join(app.instance_path, '..', 'storage', 'ppts'), exist_ok=True)
    os.makedirs(os.path.join(app.instance_path, '..', 'static', 'images'), exist_ok=True)
    
    # Register blueprints
    from app.routes.auth import bp as auth_bp
    from app.routes.main import bp as main_bp
    from app.routes.user import bp as user_bp
    from app.routes.admin import bp as admin_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Create default admin user if not exists
        from app.models.user import User
        admin_user = User.query.filter_by(email='admin@company.com').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@company.com',
                role='admin'
            )
            admin_user.set_password('admin123')  # Change this in production
            db.session.add(admin_user)
            db.session.commit()
    
    return app

@login_manager.user_loader
def load_user(user_id):
    from app.models.user import User
    return User.query.get(int(user_id))