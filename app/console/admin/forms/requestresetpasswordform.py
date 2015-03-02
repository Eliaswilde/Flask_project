from wtforms import form, fields, validators
from wtforms.validators import EqualTo
from services.user_service import UserService

user_service = UserService()

class RequestResetPasswordForm(form.Form):
    email = fields.PasswordField('email',validators=[validators.required()])

    def get_user(self):
        return user_service.get_by_email(str(self.email.data))