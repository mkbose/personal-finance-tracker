from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, DateField, SelectField, TextAreaField, SubmitField, FileField
from wtforms.validators import DataRequired, NumberRange, Length
from datetime import date

class ExpenseForm(FlaskForm):
    description = StringField('Description', validators=[DataRequired(), Length(max=200)])
    amount = FloatField('Amount', validators=[DataRequired(), NumberRange(min=0.01)])
    date = DateField('Date', validators=[DataRequired()], default=date.today)
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    subcategory_id = SelectField('Subcategory', coerce=int, default=0)
    notes = TextAreaField('Notes')
    submit = SubmitField('Save Expense')

class ImportForm(FlaskForm):
    file = FileField('CSV/Excel File', validators=[DataRequired()])
    submit = SubmitField('Import Expenses')
