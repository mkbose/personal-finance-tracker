from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Expense, Category, Subcategory, UserSettings
from app.forms.expenses import ExpenseForm
from datetime import datetime
import csv
import pandas as pd
from io import StringIO

expenses_bp = Blueprint('expenses', __name__)

@expenses_bp.route('/')
@login_required
def list_expenses():
    page = request.args.get('page', 1, type=int)
    category_id = request.args.get('category_id', type=int)
    subcategory_id = request.args.get('subcategory_id', type=int)
    amount_min = request.args.get('amount_min', type=float)
    amount_max = request.args.get('amount_max', type=float)
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    description_search = request.args.get('description_search', '')
    
    query = Expense.query.filter_by(user_id=current_user.id)
    
    # Category filter
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    # Subcategory filter (within category)
    if subcategory_id:
        query = query.filter_by(subcategory_id=subcategory_id)
    
    # Amount filters
    if amount_min is not None:
        query = query.filter(Expense.amount >= amount_min)
    if amount_max is not None:
        query = query.filter(Expense.amount <= amount_max)
    
    # Date filters
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            query = query.filter(Expense.date >= date_from_obj)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            query = query.filter(Expense.date <= date_to_obj)
        except ValueError:
            pass
    
    # Description search
    if description_search:
        query = query.filter(Expense.description.ilike(f'%{description_search}%'))
    
    expenses = query.order_by(Expense.date.desc()).paginate(
        page=page, per_page=20, error_out=False)
    
    categories = Category.query.filter_by(user_id=current_user.id).all()
    
    # Get subcategories for the selected category
    subcategories = []
    if category_id:
        subcategories = Subcategory.query.filter_by(category_id=category_id).order_by(Subcategory.name).all()
    
    # Get user settings for currency
    user_settings = UserSettings.query.filter_by(user_id=current_user.id).first()
    if not user_settings:
        user_settings = UserSettings(user_id=current_user.id)
        db.session.add(user_settings)
        db.session.commit()
    
    return render_template('expenses/list.html', 
                         expenses=expenses, 
                         categories=categories,
                         selected_category=category_id,
                         selected_subcategory=subcategory_id,
                         amount_min=amount_min,
                         amount_max=amount_max,
                         date_from=date_from,
                         date_to=date_to,
                         description_search=description_search,
                         subcategories=subcategories,
                         settings=user_settings)

@expenses_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_expense():
    form = ExpenseForm()
    form.category_id.choices = [(c.id, c.name) for c in Category.query.filter_by(user_id=current_user.id).all()]
    
    if form.category_id.data:
        subcategories = Subcategory.query.filter_by(category_id=form.category_id.data).all()
        form.subcategory_id.choices = [(0, 'None')] + [(s.id, s.name) for s in subcategories]
    
    if form.validate_on_submit():
        expense = Expense(
            description=form.description.data,
            amount=form.amount.data,
            date=form.date.data,
            category_id=form.category_id.data,
            subcategory_id=form.subcategory_id.data if form.subcategory_id.data != 0 else None,
            notes=form.notes.data,
            user_id=current_user.id
        )
        db.session.add(expense)
        db.session.commit()
        flash('Expense added successfully!')
        return redirect(url_for('expenses.list_expenses'))
    
    # Get user settings for currency
    user_settings = UserSettings.query.filter_by(user_id=current_user.id).first()
    if not user_settings:
        user_settings = UserSettings(user_id=current_user.id)
        db.session.add(user_settings)
        db.session.commit()
    
    return render_template('expenses/add.html', form=form, settings=user_settings)

@expenses_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_expense(id):
    expense = Expense.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = ExpenseForm(obj=expense)
    
    form.category_id.choices = [(c.id, c.name) for c in Category.query.filter_by(user_id=current_user.id).all()]
    
    if form.category_id.data:
        subcategories = Subcategory.query.filter_by(category_id=form.category_id.data).all()
        form.subcategory_id.choices = [(0, 'None')] + [(s.id, s.name) for s in subcategories]
    
    if form.validate_on_submit():
        expense.description = form.description.data
        expense.amount = form.amount.data
        expense.date = form.date.data
        expense.category_id = form.category_id.data
        expense.subcategory_id = form.subcategory_id.data if form.subcategory_id.data != 0 else None
        expense.notes = form.notes.data
        db.session.commit()
        flash('Expense updated successfully!')
        return redirect(url_for('expenses.list_expenses'))
    
    # Get user settings for currency
    user_settings = UserSettings.query.filter_by(user_id=current_user.id).first()
    if not user_settings:
        user_settings = UserSettings(user_id=current_user.id)
        db.session.add(user_settings)
        db.session.commit()
    
    return render_template('expenses/edit.html', form=form, expense=expense, settings=user_settings)

@expenses_bp.route('/delete/<int:id>')
@login_required
def delete_expense(id):
    expense = Expense.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(expense)
    db.session.commit()
    flash('Expense deleted successfully!')
    return redirect(url_for('expenses.list_expenses'))

@expenses_bp.route('/delete-all')
@login_required
def delete_all_expenses():
    expenses = Expense.query.filter_by(user_id=current_user.id).all()
    count = len(expenses)
    for expense in expenses:
        db.session.delete(expense)
    db.session.commit()
    flash(f'Successfully deleted {count} expenses!')
    return redirect(url_for('expenses.list_expenses'))

@expenses_bp.route('/import', methods=['GET', 'POST'])
@login_required
def import_expenses():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)
        
        if file and file.filename.endswith(('.csv', '.xlsx')):
            try:
                if file.filename.endswith('.csv'):
                    df = pd.read_csv(file)
                else:
                    df = pd.read_excel(file)
                
                required_columns = ['description', 'amount', 'date', 'category']
                if not all(col in df.columns for col in required_columns):
                    flash('File must contain columns: description, amount, date, category')
                    return render_template('expenses/import.html')
                
                for _, row in df.iterrows():
                    category = Category.query.filter_by(name=row['category'], user_id=current_user.id).first()
                    if not category:
                        category = Category(name=row['category'], user_id=current_user.id)
                        db.session.add(category)
                        db.session.flush()
                    
                    # Handle subcategory if present
                    subcategory_id = None
                    if 'subcategory' in row and pd.notna(row['subcategory']) and row['subcategory']:
                        subcategory = Subcategory.query.filter_by(
                            name=row['subcategory'], 
                            category_id=category.id
                        ).first()
                        if not subcategory:
                            subcategory = Subcategory(
                                name=row['subcategory'],
                                category_id=category.id
                            )
                            db.session.add(subcategory)
                            db.session.flush()
                        subcategory_id = subcategory.id
                    
                    expense = Expense(
                        description=row['description'],
                        amount=float(row['amount']),
                        date=pd.to_datetime(row['date']).date(),
                        category_id=category.id,
                        subcategory_id=subcategory_id,
                        user_id=current_user.id,
                        notes=row.get('notes', '')
                    )
                    db.session.add(expense)
                
                db.session.commit()
                flash(f'Successfully imported {len(df)} expenses!')
                return redirect(url_for('expenses.list_expenses'))
                
            except Exception as e:
                flash(f'Error importing file: {str(e)}')
                return render_template('expenses/import.html')
        else:
            flash('Invalid file format. Please upload CSV or Excel files.')
    
    return render_template('expenses/import.html')

@expenses_bp.route('/export')
@login_required
def export_expenses():
    expenses = Expense.query.filter_by(user_id=current_user.id).all()
    
    data = []
    for expense in expenses:
        data.append({
            'description': expense.description,
            'amount': expense.amount,
            'date': expense.date,
            'category': expense.category_obj.name,
            'subcategory': expense.subcategory_obj.name if expense.subcategory_obj else '',
            'notes': expense.notes or ''
        })
    
    df = pd.DataFrame(data)
    
    output = StringIO()
    df.to_csv(output, index=False)
    output.seek(0)
    
    return output.getvalue(), 200, {
        'Content-Type': 'text/csv',
        'Content-Disposition': 'attachment; filename=expenses.csv'
    }
