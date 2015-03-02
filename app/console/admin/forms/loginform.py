from wtforms import form, fields, validators
from services.user_service import UserService

user_service = UserService()

class LoginForm(form.Form):
    email = fields.TextField(validators=[validators.required()])
    password = fields.PasswordField(validators=[validators.required()])

    def validate_login(self, field):
        user = self.get_user()

        if user is None:
            raise validators.ValidationError('Invalid user')

        if user.password != self.password.data:
            raise validators.ValidationError('Invalid password')

    def get_user(self):
        return user_service.get_by_email(str(self.email.data)) #db.session.query(User).filter_by(login=self.email.data).first()