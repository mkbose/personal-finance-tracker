from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Category, Subcategory, Expense
from app.forms.categories import CategoryForm, SubcategoryForm

categories_bp = Blueprint('categories', __name__)

@categories_bp.route('/')
@login_required
def list_categories():
    categories = Category.query.filter_by(user_id=current_user.id)\
        .order_by(Category.name).all()
    return render_template('categories/list.html', categories=categories)

@categories_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_category():
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(
            name=form.name.data,
            description=form.description.data,
            user_id=current_user.id
        )
        db.session.add(category)
        db.session.commit()
        flash('Category added successfully!')
        return redirect(url_for('categories.list_categories'))
    
    return render_template('categories/add.html', form=form)

@categories_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_category(id):
    category = Category.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = CategoryForm(obj=category)
    
    if form.validate_on_submit():
        category.name = form.name.data
        category.description = form.description.data
        db.session.commit()
        flash('Category updated successfully!')
        return redirect(url_for('categories.list_categories'))
    
    return render_template('categories/edit.html', form=form, category=category)

@categories_bp.route('/delete/<int:id>')
@login_required
def delete_category(id):
    category = Category.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    if category.expenses:
        flash('Cannot delete category with associated expenses. Please delete or reassign expenses first.')
        return redirect(url_for('categories.list_categories'))
    
    db.session.delete(category)
    db.session.commit()
    flash('Category deleted successfully!')
    return redirect(url_for('categories.list_categories'))

@categories_bp.route('/<int:category_id>/subcategories')
@login_required
def list_subcategories(category_id):
    category = Category.query.filter_by(id=category_id, user_id=current_user.id).first_or_404()
    subcategories = Subcategory.query.filter_by(category_id=category_id)\
        .order_by(Subcategory.name).all()
    return render_template('categories/subcategories/list.html', 
                         category=category, subcategories=subcategories)

@categories_bp.route('/<int:category_id>/subcategories/add', methods=['GET', 'POST'])
@login_required
def add_subcategory(category_id):
    category = Category.query.filter_by(id=category_id, user_id=current_user.id).first_or_404()
    form = SubcategoryForm()
    
    if form.validate_on_submit():
        subcategory = Subcategory(
            name=form.name.data,
            category_id=category_id
        )
        db.session.add(subcategory)
        db.session.commit()
        flash('Subcategory added successfully!')
        return redirect(url_for('categories.list_subcategories', category_id=category_id))
    
    return render_template('categories/subcategories/add.html', 
                         form=form, category=category)

@categories_bp.route('/subcategories/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_subcategory(id):
    subcategory = Subcategory.query.join(Category).filter(
        Subcategory.id == id, 
        Category.user_id == current_user.id
    ).first_or_404()
    
    form = SubcategoryForm(obj=subcategory)
    
    if form.validate_on_submit():
        subcategory.name = form.name.data
        db.session.commit()
        flash('Subcategory updated successfully!')
        return redirect(url_for('categories.list_subcategories', 
                               category_id=subcategory.category_id))
    
    return render_template('categories/subcategories/edit.html', 
                         form=form, subcategory=subcategory)

@categories_bp.route('/subcategories/delete/<int:id>')
@login_required
def delete_subcategory(id):
    subcategory = Subcategory.query.join(Category).filter(
        Subcategory.id == id, 
        Category.user_id == current_user.id
    ).first_or_404()
    category_id = subcategory.category_id
    db.session.delete(subcategory)
    db.session.commit()
    flash('Subcategory deleted successfully!')
    return redirect(url_for('categories.list_subcategories', category_id=category_id))

@categories_bp.route('/<int:category_id>/subcategories/json')
@login_required
def get_subcategories_json(category_id):
    category = Category.query.filter_by(id=category_id, user_id=current_user.id).first_or_404()
    subcategories = Subcategory.query.filter_by(category_id=category_id)\
        .order_by(Subcategory.name).all()
    
    return jsonify([{'id': s.id, 'name': s.name} for s in subcategories])

@categories_bp.route('/merge', methods=['GET', 'POST'])
@login_required
def merge_categories():
    if request.method == 'POST':
        source_id = request.form.get('source_category')
        target_id = request.form.get('target_category')
        
        if source_id == target_id:
            flash('Source and target categories must be different!')
            return redirect(url_for('categories.list_categories'))
        
        source_category = Category.query.filter_by(id=source_id, user_id=current_user.id).first_or_404()
        target_category = Category.query.filter_by(id=target_id, user_id=current_user.id).first_or_404()
        
        # Update all expenses from source category to target category
        Expense.query.filter_by(category_id=source_id, user_id=current_user.id).update({'category_id': target_id})
        
        # Update all subcategories from source category to target category with unique names
        source_subcategories = Subcategory.query.filter_by(category_id=source_id).all()
        for subcategory in source_subcategories:
            # Make subcategory name unique by appending source category name
            new_name = f"{subcategory.name} (from {source_category.name})"
            # Check if this name already exists in target category
            existing = Subcategory.query.filter_by(
                name=new_name, 
                category_id=target_id
            ).first()
            if existing:
                # Add a number to make it unique
                counter = 1
                while existing:
                    new_name = f"{subcategory.name} (from {source_category.name}) {counter}"
                    existing = Subcategory.query.filter_by(
                        name=new_name, 
                        category_id=target_id
                    ).first()
                    counter += 1
            
            subcategory.name = new_name
            subcategory.category_id = target_id
        
        db.session.commit()
        
        # Delete the source category
        db.session.delete(source_category)
        db.session.commit()
        
        flash(f'Successfully merged "{source_category.name}" into "{target_category.name}"!')
        return redirect(url_for('categories.list_categories'))
    
    categories = Category.query.filter_by(user_id=current_user.id).order_by(Category.name).all()
    return render_template('categories/merge.html', categories=categories)

@categories_bp.route('/subcategories/merge/<int:category_id>', methods=['GET', 'POST'])
@login_required
def merge_subcategories(category_id):
    category = Category.query.filter_by(id=category_id, user_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        source_id = request.form.get('source_subcategory')
        target_id = request.form.get('target_subcategory')
        
        if source_id == target_id:
            flash('Source and target subcategories must be different!')
            return redirect(url_for('categories.list_subcategories', category_id=category_id))
        
        source_subcategory = Subcategory.query.filter_by(id=source_id, category_id=category_id).first_or_404()
        target_subcategory = Subcategory.query.filter_by(id=target_id, category_id=category_id).first_or_404()
        
        # Update all expenses from source subcategory to target subcategory
        Expense.query.filter_by(subcategory_id=source_id, user_id=current_user.id).update({'subcategory_id': target_id})
        
        # Delete the source subcategory
        db.session.delete(source_subcategory)
        db.session.commit()
        
        flash(f'Successfully merged "{source_subcategory.name}" into "{target_subcategory.name}"!')
        return redirect(url_for('categories.list_subcategories', category_id=category_id))
    
    subcategories = Subcategory.query.filter_by(category_id=category_id).order_by(Subcategory.name).all()
    return render_template('categories/subcategories/merge.html', category=category, subcategories=subcategories)
