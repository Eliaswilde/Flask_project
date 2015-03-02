from flask_wtf import Form
from wtforms.fields import *
from wtforms.validators import *
from wtforms.validators import ValidationError
from app.console.admin.helpers import COUNTRIES, STATES

class RequiredIfNot(Required):
    # a validator which makes a field required if
    # another field is set and has a truthy value

    def __init__(self, other_field_name, *args, **kwargs):
        self.other_field_name = other_field_name
        super(RequiredIfNot, self).__init__(*args, **kwargs)

    def __call__(self, form, field):
        other_field = form._fields.get(self.other_field_name)
        if other_field is None:
            raise Exception('no field named "%s" in form' % self.other_field_name)
        if not bool(other_field.data):
            super(RequiredIfNot, self).__call__(form, field)

class OptionalForm(Form):
    is_form_optional = False

    def validate(self, extra_validators=tuple()):
        if self.is_form_optional:
            return True
        return super(OptionalForm, self).validate()


class CheckoutAnonForm(OptionalForm):
    fullname = TextField('Full Name',validators=[DataRequired()])
    email = TextField(validators=[DataRequired()])
    opt_in = BooleanField()
    display_name = BooleanField()

class CheckoutShippingForm(OptionalForm):
    firstname = TextField('First Name',validators=[DataRequired()])
    lastname = TextField('Last Name',validators=[DataRequired()])
    address = TextField(validators=[length(max=100),DataRequired()])
    city = TextField(validators=[length(max=100),DataRequired()])
    state = SelectField('State / Province', choices=STATES)
    state_custom = TextField('State / Province', validators=[length(max=100)])
    postal_code = TextField('Zip / Postal Code', validators=[length(max=100),DataRequired()])
    country = SelectField('Country', choices=COUNTRIES, default='US',validators=[DataRequired()])
    
    def validate_state(form, field):
        if form.country.data == 'US' and not field.data:
            raise ValidationError(u'Enter your state')
    
    def validate_state_custom(form, field):
        if form.country.data != 'US' and not field.data:
            raise ValidationError(u'Enter your state')

class CheckoutForm(Form):
    contributionamount = TextField(validators=[RequiredIfNot('reward_id')],default=0)
    reward_id = HiddenField(validators=[RequiredIfNot('contributionamount')])
    anon_info = FormField(CheckoutAnonForm)
    shipping_info = FormField(CheckoutShippingForm)