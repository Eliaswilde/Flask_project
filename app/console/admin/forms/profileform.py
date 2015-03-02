from flask_wtf import Form
from wtforms.fields import *
from wtforms.validators import *
from services.user_service import UserService

from app.console.admin.fields.fields import BCDateField
from app.console.admin.helpers import COUNTRIES, STATES


user_service = UserService()

class RequiredIf(Required):
    # a validator which makes a field required if
    # another field is set and has a truthy value

    def __init__(self, other_field_name, *args, **kwargs):
        self.other_field_name = other_field_name
        super(RequiredIf, self).__init__(*args, **kwargs)

    def __call__(self, form, field):
        other_field = form._fields.get(self.other_field_name)
        if other_field is None:
            raise Exception('no field named "%s" in form' % self.other_field_name)
        if bool(other_field.data):
            super(RequiredIf, self).__call__(form, field)

class ContactForm(Form):
    optional = False

    phone_number = TextField(validators=[length(max=100)])
    address = TextField(validators=[length(max=100),required()])
    city = TextField(validators=[length(max=100)])
    state = SelectField('State / Province', choices=STATES)
    state_custom = TextField('State / Province', validators=[length(max=100)])
    postal_code = TextField('Zip / Postal Code', validators=[length(max=100)])
    country = SelectField('Country', choices=COUNTRIES, default='US')

    def validate(self, extra_validators=tuple()):
        if optional:
            return True
        return self.form.validate()


class ProfileForm(Form):

    company_name = TextField(validators=[length(max=100)])
    title = TextField(validators=[length(max=100)])
    first_name = TextField(validators=[required(), length(max=100)])
    last_name = TextField(validators=[required(), length(max=100)])
    email = TextField(validators=[required(), email()])
    birth_date = BCDateField()
    bio = TextAreaField('Short Bio', validators=[length(max=500)])
    shipping_info = FormField(ContactForm)
    billing_info = FormField(ContactForm)
    billing_equals_shipping = BooleanField()

    fb_profile = TextField('Facebook Profile', validators=[length(max=200)])
    linkedin_profile = TextField('LinkedIn Profile', validators=[length(max=200)])
    twitter_profile = TextField('Twitter Profile', validators=[length(max=200)])
    youtube_profile = TextField('YouTube Profile', validators=[length(max=200)])
    imdb_profile = TextField('IMDB Profile', validators=[length(max=200)])
    website_profile = TextField('Your Website', validators=[length(max=200)])

    avatar = HiddenField()




