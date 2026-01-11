from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange, Optional

class SettingsForm(FlaskForm):
    # Currency Settings
    currency_symbol = StringField('Currency Symbol', validators=[DataRequired(), Length(max=10)])
    currency_code = SelectField('Currency Code', choices=[
        ('USD', 'USD - US Dollar'),
        ('EUR', 'EUR - Euro'),
        ('GBP', 'GBP - British Pound'),
        ('INR', 'INR - Indian Rupee'),
        ('JPY', 'JPY - Japanese Yen'),
        ('CNY', 'CNY - Chinese Yuan'),
        ('CAD', 'CAD - Canadian Dollar'),
        ('AUD', 'AUD - Australian Dollar')
    ])
    decimal_places = IntegerField('Decimal Places', validators=[DataRequired(), NumberRange(min=0, max=4)])
    
    # Theme Settings
    theme = SelectField('Theme', choices=[
        ('light', 'Light Theme'),
        ('dark', 'Dark Theme'),
        ('auto', 'Auto (System Preference)')
    ])
    primary_color = StringField('Primary Color', validators=[DataRequired(), Length(max=7)])
    secondary_color = StringField('Secondary Color', validators=[DataRequired(), Length(max=7)])
    
    # Dashboard Settings
    default_date_range = SelectField('Default Date Range', choices=[
        ('all_time', 'All Time'),
        ('last_30_days', 'Last 30 Days'),
        ('last_month', 'Last Month'),
        ('current_year', 'Current Year')
    ])
    chart_type = SelectField('Default Chart Type', choices=[
        ('pie', 'Pie Chart'),
        ('bar', 'Bar Chart'),
        ('doughnut', 'Doughnut Chart')
    ])
    
    # Notification Settings
    email_notifications = BooleanField('Email Notifications')
    monthly_reports = BooleanField('Monthly Reports')
    
    # Display Settings
    items_per_page = SelectField('Items Per Page', choices=[
        ('5', '5'),
        ('10', '10'),
        ('25', '25'),
        ('50', '50'),
        ('100', '100')
    ])
    date_format = SelectField('Date Format', choices=[
        ('%Y-%m-%d', 'YYYY-MM-DD'),
        ('%d/%m/%Y', 'DD/MM/YYYY'),
        ('%m/%d/%Y', 'MM/DD/YYYY'),
        ('%d-%b-%Y', 'DD-Mon-YYYY'),
        ('%B %d, %Y', 'Month DD, YYYY')
    ])
