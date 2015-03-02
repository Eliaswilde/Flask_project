from flask import url_for
from flask.ext.admin import form
from flask.ext import login
from flask.ext.admin.contrib import sqla
from markupsafe import Markup
from wtforms import SelectField
from app.console.admin.BCModelView import BCModelView
from app.console.admin.fields.fields import BCDateField


class UserView(BCModelView):

    def _user_type(view, context, model, name):
        choices=[(0, 'backer'), (1, 'producer'), (2, 'admin')]
        return choices[model.user_type][1]

    column_list = ('username', 'first_name', 'last_name','email','phone','date')
    column_searchable_list = ('username', 'first_name', 'last_name','email')
    #column_filters = ['username',]
    form_excluded_columns = ['shipping_info' ,'billing_info' ,'comments','teammember','campaigns','campaign',]

    #form_extra_fields = {
    #    'birth_date': BCDateField('Birth Date'),
    #}

    #form_create_rules = ('email', 'first_name', 'last_name','user_type')
    form_columns = ('email','username', 'first_name', 'last_name','password','user_type')
    form_overrides = dict(user_type=SelectField)
    form_args = dict(
        user_type=dict(
            choices=[(0, 'backer'), (1, 'producer'), (2, 'admin')],coerce=int
        ))

   # form_overrides = {
    #    'path': form.ImageUploadField
   # }
    # Alternative way to contribute field is to override it completely.
    # In this case, Flask-Admin won't attempt to merge various parameters for the field.

