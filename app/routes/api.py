from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app import db
from app.models import Expense, Category, Subcategory
from sqlalchemy import func, extract
from datetime import datetime, timedelta
import calendar

api_bp = Blueprint('api', __name__)

@api_bp.route('/dashboard/stats')
@login_required
def dashboard_stats():
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    # Monthly total
    monthly_total = db.session.query(func.sum(Expense.amount)).filter(
        Expense.user_id == current_user.id,
        extract('month', Expense.date) == current_month,
        extract('year', Expense.date) == current_year
    ).scalar() or 0
    
    # Last 30 days total
    thirty_days_ago = datetime.now().date() - timedelta(days=30)
    recent_total = db.session.query(func.sum(Expense.amount)).filter(
        Expense.user_id == current_user.id,
        Expense.date >= thirty_days_ago
    ).scalar() or 0
    
    # Category breakdown for current month
    category_breakdown = db.session.query(
        Category.name,
        func.sum(Expense.amount).label('total')
    ).join(Expense).filter(
        Expense.user_id == current_user.id,
        extract('month', Expense.date) == current_month,
        extract('year', Expense.date) == current_year
    ).group_by(Category.name).all()
    
    # Daily expenses for last 30 days
    daily_expenses = db.session.query(
        Expense.date,
        func.sum(Expense.amount).label('total')
    ).filter(
        Expense.user_id == current_user.id,
        Expense.date >= thirty_days_ago
    ).group_by(Expense.date).order_by(Expense.date).all()
    
    return jsonify({
        'monthly_total': float(monthly_total),
        'recent_total': float(recent_total),
        'category_breakdown': [{'name': name, 'total': float(total)} for name, total in category_breakdown],
        'daily_expenses': [{'date': date.isoformat(), 'total': float(total)} for date, total in daily_expenses]
    })

@api_bp.route('/debug/expenses')
def debug_expenses():
    # Debug endpoint without authentication to check data
    try:
        # Get all expenses to see what's in database
        all_expenses = Expense.query.all()
        total_amount = sum(exp.amount for exp in all_expenses)
        
        # Get date range info
        if all_expenses:
            dates = [exp.date for exp in all_expenses]
            min_date = min(dates)
            max_date = max(dates)
        else:
            min_date = max_date = None
        
        return jsonify({
            'total_expenses': len(all_expenses),
            'total_amount': float(total_amount),
            'date_range': {
                'min': min_date.isoformat() if min_date else None,
                'max': max_date.isoformat() if max_date else None
            },
            'sample_expenses': [
                {
                    'description': exp.description, 
                    'amount': exp.amount, 
                    'category': exp.category_obj.name if exp.category_obj else 'No Category',
                    'date': exp.date.isoformat()
                } 
                for exp in all_expenses[:5]
            ]
        })
    except Exception as e:
        return jsonify({'error': str(e)})

@api_bp.route('/expenses/test-data')
@login_required
def test_data():
    # Simple test to see if we have any expenses
    total_expenses = Expense.query.filter_by(user_id=current_user.id).count()
    total_amount = db.session.query(func.sum(Expense.amount)).filter_by(user_id=current_user.id).scalar() or 0
    
    return jsonify({
        'total_expenses': total_expenses,
        'total_amount': float(total_amount),
        'message': f'Found {total_expenses} expenses totaling ₹{total_amount:.2f}'
    })

@api_bp.route('/expenses/custom-range')
@login_required
def custom_range():
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    # If no date range, return grand total of all expenses
    if not date_from and not date_to:
        total = db.session.query(func.sum(Expense.amount)).filter_by(user_id=current_user.id).scalar() or 0
        return jsonify({'total': float(total)})
    
    if not date_from or not date_to:
        return jsonify({'total': 0})
    
    try:
        date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
        date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'total': 0})
    
    # Get total expenses for custom date range
    total = db.session.query(func.sum(Expense.amount)).filter(
        Expense.user_id == current_user.id,
        Expense.date >= date_from_obj,
        Expense.date <= date_to_obj
    ).scalar() or 0
    
    return jsonify({'total': float(total)})

@api_bp.route('/expenses/monthly-trend')
@login_required
def monthly_trend():
    # Get last 12 months data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    monthly_data = db.session.query(
        extract('year', Expense.date).label('year'),
        extract('month', Expense.date).label('month'),
        func.sum(Expense.amount).label('total')
    ).filter(
        Expense.user_id == current_user.id,
        Expense.date >= start_date.date()
    ).group_by(
        extract('year', Expense.date),
        extract('month', Expense.date)
    ).order_by(
        extract('year', Expense.date),
        extract('month', Expense.date)
    ).all()
    
    trend_data = []
    for year, month, total in monthly_data:
        month_name = calendar.month_name[int(month)]
        trend_data.append({
            'month': f'{month_name} {int(year)}',
            'total': float(total)
        })
    
    return jsonify(trend_data)

@api_bp.route('/expenses/category-comparison')
@login_required
def category_comparison():
    # Compare categories across last 3 months
    current_date = datetime.now()
    three_months_ago = current_date - timedelta(days=90)
    
    comparison_data = db.session.query(
        Category.name,
        func.sum(Expense.amount).label('total'),
        func.count(Expense.id).label('count')
    ).join(Expense).filter(
        Expense.user_id == current_user.id,
        Expense.date >= three_months_ago.date()
    ).group_by(Category.name).order_by(func.sum(Expense.amount).desc()).all()
    
    return jsonify([{
        'name': name,
        'total': float(total),
        'count': count
    } for name, total, count in comparison_data])
