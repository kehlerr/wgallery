from flask_wtf import FlaskForm
from wtforms import StringField, validators


class EditModalForm(FlaskForm):
    '''
        Form for edit modal(s) with fields:
        - for entered new catalog type;
        - for entered new catalog category.
    '''
    new_type_name = StringField('', id='input-type-name')
    new_category_name = StringField('', id='input-category-name')
