from flask.ext.wtf import Form
from wtforms import TextField, PasswordField, BooleanField
from wtforms.validators import Required, Email, ValidationError
from models import User
    
class LoginForm(Form):
    email = TextField(u"E-Mail Address*", [Required(), Email()])
    password = PasswordField(u"Password*", [Required()])
    remember_me = BooleanField(u"Remember me")

class SignupForm(Form):
    first_name = TextField(u"First Name*", [Required()])
    last_name = TextField(u"Last Name*", [Required()])
    email = TextField(u"E-Mail Address*", [Required(), Email()])
    password = PasswordField(u"Password*", [Required()])
    receive_news = BooleanField(u"Receive Insider News to pre release deals and exclusive access")
    
    def validate_email(form, field):
        existing_user = User.query.filter_by(email=field.data).first()
        if existing_user:
            raise ValidationError(u'User with this email is already registered.')
