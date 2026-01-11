from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import Expense, Category, Subcategory
from sqlalchemy import func, extract
from datetime import datetime, timedelta
import calendar

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    print(f"DEBUG: Dashboard route accessed by user {current_user.id}")
    
    # Get all-time data instead of current month
    monthly_total = db.session.query(func.sum(Expense.amount)).filter_by(user_id=current_user.id).scalar() or 0
    recent_total = db.session.query(func.sum(Expense.amount)).filter(
        Expense.user_id == current_user.id,
        Expense.date >= (datetime.now().date() - timedelta(days=30))
    ).scalar() or 0
    
    # Get category breakdown for all time
    category_breakdown_raw = db.session.query(
        Category.name,
        func.sum(Expense.amount).label('total')
    ).join(Expense).filter(
        Expense.user_id == current_user.id
    ).group_by(Category.name).all()
    
    # Convert to serializable format
    category_breakdown = [{'name': name, 'total': float(total)} for name, total in category_breakdown_raw]
    
    # Get recent expenses
    recent_expenses = Expense.query.filter_by(user_id=current_user.id)\
        .order_by(Expense.date.desc()).limit(5).all()
    
    # Get total expenses count
    total_expenses = Expense.query.filter_by(user_id=current_user.id).count()
    
    print(f"DEBUG: All-time monthly total: {monthly_total}")
    print(f"DEBUG: Recent total: {recent_total}")
    print(f"DEBUG: Category breakdown items: {len(category_breakdown)}")
    
    return render_template('dashboard.html',
                         monthly_total=monthly_total,
                         recent_total=recent_total,
                         category_breakdown=category_breakdown,
                         recent_expenses=recent_expenses,
                         total_expenses=total_expenses)

@main_bp.route('/create-sample-data')
@login_required
def create_sample_data():
    # Create sample categories
    food_category = Category(name='Food & Dining', user_id=current_user.id)
    transport_category = Category(name='Transportation', user_id=current_user.id)
    entertainment_category = Category(name='Entertainment', user_id=current_user.id)
    
    db.session.add_all([food_category, transport_category, entertainment_category])
    db.session.flush()
    
    # Create sample expenses
    from datetime import date
    sample_expenses = [
        Expense(
            description='Coffee Shop',
            amount=4.50,
            date=date(2024, 1, 15),
            category_id=food_category.id,
            user_id=current_user.id,
            notes='Morning coffee'
        ),
        Expense(
            description='Gas Station',
            amount=45.00,
            date=date(2024, 1, 14),
            category_id=transport_category.id,
            user_id=current_user.id,
            notes='Full tank'
        ),
        Expense(
            description='Netflix Subscription',
            amount=15.99,
            date=date(2024, 1, 10),
            category_id=entertainment_category.id,
            user_id=current_user.id,
            notes='Monthly fee'
        )
    ]
    
    db.session.add_all(sample_expenses)
    db.session.commit()
    
    flash('Sample data created! 3 categories and 3 expenses added.')
    return redirect(url_for('main.dashboard'))
