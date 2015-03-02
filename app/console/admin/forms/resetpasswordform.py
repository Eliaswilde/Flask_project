from wtforms import form, fields, validators
from wtforms.validators import EqualTo
from services.user_service import UserService

user_service = UserService()

class ResetPasswordForm(form.Form):
    password = fields.PasswordField('password',validators=[validators.required()])
    confirm = fields.PasswordField('confirm',validators=[validators.required()])
    reset_hash = fields.HiddenField('reset_hash',validators=[validators.required()])
