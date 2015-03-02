from wtforms.form import Form
from wtforms.fields import *
from wtforms.validators import *
from services.user_service import UserService

from app.validators import unique
from models import User


user_service = UserService()

MSG_USERNAME = 'User with this username is already registered'
MSG_EMAIL = 'User with this email is already registered'


class RegistrationForm(Form):
    first_name = TextField(validators=[required(), length(max=100)])
    last_name = TextField(validators=[required(), length(max=100)])
    username = TextField(validators=[required(), length(max=80),
                                     unique(User, User.username,
                                            message=MSG_USERNAME)])
    email = TextField(validators=[required(), email(),
                                  unique(User, User.email, message=MSG_EMAIL)])
    password = PasswordField(validators=[required(), length(max=80)])
    confirm = PasswordField('Repeat Password', validators=[
        equal_to('password', message='Passwords must match')])

    def get_user(self):
        return user_service.get_by_email(str(self.email.data))
