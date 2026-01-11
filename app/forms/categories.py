from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length

class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description')
    submit = SubmitField('Save Category')

class SubcategoryForm(FlaskForm):
    name = StringField('Subcategory Name', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Save Subcategory')

class MergeForm(FlaskForm):
    source_category = SelectField('Source Category', coerce=int, validators=[DataRequired()])
    target_category = SelectField('Target Category', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Merge Categories')
