from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    expenses = db.relationship('Expense', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    subcategories = db.relationship('Subcategory', backref='category', lazy=True, cascade='all, delete-orphan')
    expenses = db.relationship('Expense', backref='category_obj', lazy=True)
    
    __table_args__ = (db.UniqueConstraint('name', 'user_id', name='unique_category_user'),)

class Subcategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    expenses = db.relationship('Expense', backref='subcategory_obj', lazy=True)
    
    __table_args__ = (db.UniqueConstraint('name', 'category_id', name='unique_subcategory_category'),)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date())
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    subcategory_id = db.Column(db.Integer, db.ForeignKey('subcategory.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class UserSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Currency settings
    currency_symbol = db.Column(db.String(10), default='₹')
    currency_code = db.Column(db.String(3), default='INR')
    decimal_places = db.Column(db.Integer, default=2)
    
    # Theme settings
    theme = db.Column(db.String(20), default='light')  # light, dark, auto
    primary_color = db.Column(db.String(7), default='#007bff')
    secondary_color = db.Column(db.String(7), default='#6c757d')
    
    # Dashboard settings
    default_date_range = db.Column(db.String(20), default='all_time')  # all_time, last_30_days, last_month
    chart_type = db.Column(db.String(20), default='pie')  # pie, bar, doughnut
    
    # Notification settings
    email_notifications = db.Column(db.Boolean, default=True)
    monthly_reports = db.Column(db.Boolean, default=True)
    
    # Display settings
    items_per_page = db.Column(db.Integer, default=10)
    date_format = db.Column(db.String(20), default='%Y-%m-%d')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('settings', lazy=True, uselist=False))
    
    def __repr__(self):
        return f'<UserSettings {self.user_id}>'
