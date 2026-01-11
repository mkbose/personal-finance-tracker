from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    
    # Set locale to ensure USD formatting
    app.config['BABEL_DEFAULT_LOCALE'] = 'en_US'
    app.config['BABEL_DEFAULT_TIMEZONE'] = 'UTC'
    
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///finance.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = 'uploads'
    
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.expenses import expenses_bp
    from app.routes.categories import categories_bp
    from app.routes.api import api_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(expenses_bp, url_prefix='/expenses')
    app.register_blueprint(categories_bp, url_prefix='/categories')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    with app.app_context():
        from app.models import User, Expense, Category, Subcategory
        db.create_all()
    
    return app
