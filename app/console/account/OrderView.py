from flask import url_for
from flask.ext.admin import form
from flask.ext import login
from flask.ext.admin.contrib import sqla
from markupsafe import Markup
from wtforms import SelectField
from app.console.admin.BCModelView import BCModelView
from app.console.admin.fields.fields import BCDateField


class OrderView(BCModelView):

    pass

   # form_overrides = {
    #    'path': form.ImageUploadField
   # }
    # Alternative way to contribute field is to override it completely.
    # In this case, Flask-Admin won't attempt to merge various parameters for the field.

