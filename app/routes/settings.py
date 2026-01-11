from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import UserSettings
from app.forms.settings import SettingsForm

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    # Get or create user settings
    user_settings = UserSettings.query.filter_by(user_id=current_user.id).first()
    if not user_settings:
        user_settings = UserSettings(
            user_id=current_user.id,
            currency_symbol='₹',
            currency_code='INR',
            theme='light',
            primary_color='#007bff',
            secondary_color='#6c757d'
        )
        db.session.add(user_settings)
        db.session.commit()
    
    form = SettingsForm(obj=user_settings)
    
    if form.validate_on_submit():
        # Auto-populate currency symbol based on currency code if not manually set
        currency_symbols = {
            'USD': '$',
            'EUR': '€',
            'GBP': '£',
            'INR': '₹',
            'JPY': '¥',
            'CNY': '¥',
            'CAD': 'C$',
            'AUD': 'A$'
        }
        
        # Update settings
        user_settings.currency_symbol = form.currency_symbol.data
        user_settings.currency_code = form.currency_code.data
        user_settings.decimal_places = form.decimal_places.data
        user_settings.theme = form.theme.data
        user_settings.primary_color = form.primary_color.data
        user_settings.secondary_color = form.secondary_color.data
        user_settings.default_date_range = form.default_date_range.data
        user_settings.chart_type = form.chart_type.data
        user_settings.email_notifications = form.email_notifications.data
        user_settings.monthly_reports = form.monthly_reports.data
        user_settings.items_per_page = int(form.items_per_page.data)
        user_settings.date_format = form.date_format.data
        
        db.session.commit()
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('settings.settings'))
    
    return render_template('settings/index.html', form=form, settings=user_settings)

@settings_bp.route('/settings/reset')
@login_required
def reset_settings():
    # Reset to default settings
    user_settings = UserSettings.query.filter_by(user_id=current_user.id).first()
    if user_settings:
        user_settings.currency_symbol = '₹'
        user_settings.currency_code = 'INR'
        user_settings.decimal_places = 2
        user_settings.theme = 'light'
        user_settings.primary_color = '#007bff'
        user_settings.secondary_color = '#6c757d'
        user_settings.default_date_range = 'all_time'
        user_settings.chart_type = 'pie'
        user_settings.email_notifications = True
        user_settings.monthly_reports = True
        user_settings.items_per_page = 10
        user_settings.date_format = '%Y-%m-%d'
        
        db.session.commit()
        flash('Settings reset to defaults!', 'info')
    
    return redirect(url_for('settings.settings'))

@settings_bp.route('/settings/preview-theme')
@login_required
def preview_theme():
    theme = request.args.get('theme', 'light')
    primary_color = request.args.get('primary_color', '#007bff')
    secondary_color = request.args.get('secondary_color', '#6c757d')
    
    return render_template('settings/preview.html', 
                         theme=theme, 
                         primary_color=primary_color, 
                         secondary_color=secondary_color)
