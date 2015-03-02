from flask_wtf import Form
from wtforms import validators, ValidationError
from wtforms.fields import *
from wtforms.validators import *
from wtforms.validators import ValidationError
from app.console.admin.fields.fields import BCDateField
from urlparse import urlparse
from flask import json



{"form_launch" : { },
    "form_campaign_info" : {
      "description" : "shortshortshort",
      "full_description" : "full",
      "campaign_title" : "title",
      "video_link_1" : "vlink1",
      "video_link_3" : "vlink3",
      "video_link_2" : "vlink2"
    }}

{"form_rewards" : [{
        "id" : "1",
        "quantity" : "1",
        "dollar_amount" : "123",
        "name" : "name",
        "expiration" : " 10/20/1982",
        "has_quantity" : "on",
        "description" : "desc",
        "delivery_date" : " 10/20/1982"
      }]}

{ "form_paid" : {
      "phone_number" : "3106190242",
      "city" : "city",
      "first_name" : "fname",
      "last_name" : "lname",
      "promo_code" : "code",
      "zip" : "zip",
      "legal_last_name" : "ll",
      "dob" : " 10/20/1982",
      "wepay_email" : "wemeail",
      "state" : "state",
      "company_name" : "name",
      "address" : "address",
      "legal_first_name" : "lf"
    },}

{"form_basics" : {
      "category" : "3",
      "campaign_reciever" : "non_profit",
      "campaign_type" : "flexible",
      "dollar_amount" : "eqwe",
      "campaign_management" : "on",
      "deadline" : " 10/20/1982",
      "fulfillment_service" : "on",
      "evergreen_campaign_page" : "on"
    }}

#validators=[validators.required()]


CATEGORIES = [
    ('', ''),
    ('1', 'Movie / Film'),
    ('2', 'Web Series'),
    ('3', 'TV Show'),
    ('4', 'Interactive Media / Games'),
    ('5', 'Live Performance'),
    ('6', 'Experiences'),
    ('7', 'Other'),
]

RECEIVERS = [
    ('1', 'idividual'),
    ('2', 'registered'),
    ('3', 'non_profit'),
]

CAMPAIGN_TYPE = [
    ('1', 'Flexible Goal'),
    ('2', 'Fixed Goal'),
    ('3', 'No Goal'),
]

ACCOUNT_PAYMENT_TYPE = [
    ('1', 'Idividual'),
    ('2', 'Business'),
]

REFERRAL_COUNT = [
     (str(i), str(i)) for i in range(1, 25)
]

class DollarField(DecimalField):

    def process_formdata(self, valuelist):
        if len(valuelist) == 1:
            self.data = [valuelist[0].strip('$').replace(',', '')]
        else:
            self.data = []

        super(DollarField,self).process_formdata(self.data)

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

class CampaignForm(Form):
    csrf_enabled=False

class CampaignBasicForm(CampaignForm):
    category_id = SelectField( choices=CATEGORIES)
    campaign_receiver_id = SelectField(choices=RECEIVERS,validators=[validators.required()])
    dollar_amount = DollarField(validators=[validators.required()])
    campaign_type_id = SelectField(choices=CAMPAIGN_TYPE,validators=[validators.required()])
    fulfillment_service = BooleanField()
    campaign_management = BooleanField()
    evergreen_campaign_page = BooleanField()
    deadline = BCDateField()

class CampaignPaidForm(CampaignForm):
    phone_number = TextField(validators=[validators.required()])
    city = TextField(validators=[validators.required()])
    first_name = TextField(validators=[validators.required()])
    last_name = TextField(validators=[validators.required()])
    promo_code = TextField()
    zip = TextField(validators=[validators.required()])
    legal_last_name = TextField(validators=[validators.required()])
    legal_first_name = TextField(validators=[validators.required()])
    dob = TextField(validators=[validators.required()])
    paypal_email = TextField(validators=[validators.required()])
    state = TextField(validators=[validators.required()])
    company_name = TextField(validators=[validators.required()])
    address = TextField(validators=[validators.required()])
    pay_to_name = TextField(validators=[validators.required()])

class CampaignRewardForm(CampaignForm):
    id = TextField(validators=[validators.required()])
    dollar_amount = DollarField(validators=[validators.required()])
    quantity = IntegerField(validators=[RequiredIf('limited_quantity'),validators.Optional()],default=-1)
    expiration = BCDateField()
    name = TextField(validators=[validators.required(),length(max=100,min=5)])
    description = TextField(validators=[validators.required(),length(max=2048,min=10)])
    delivery_date = BCDateField()
    shipping_required = BooleanField()
    limited_quantity = BooleanField()
    is_featured = BooleanField()
    thumbnail_url = TextField(validators=[length(max=512)])
    shipping_fee = DollarField(validators=[RequiredIf('shipping_required'),validators.Optional()])
    international_shipping_fee = DollarField(validators=[RequiredIf('shipping_required'),validators.Optional()])


class CampaignBonusRewardForm(CampaignForm):
    referrals_needed = SelectField(choices=REFERRAL_COUNT,validators=[validators.required()])
    quantity = IntegerField(validators=[RequiredIf('limited_quantity'),validators.Optional()])
    name = TextField(validators=[validators.required(),length(max=100,min=5)])
    description = TextField(validators=[validators.required(),length(max=2048,min=10)])
    delivery_date = BCDateField()
    shipping_required = BooleanField()
    limited_quantity = BooleanField()
    thumbnail_url = TextField(validators=[length(max=512)])
    shipping_fee = DollarField(validators=[RequiredIf('shipping_required'),validators.Optional()])
    international_shipping_fee = DollarField(validators=[RequiredIf('shipping_required'),validators.Optional()])

class CampaignConfirmationMessageForm(CampaignForm):
    confirmation_message = TextField(validators=[validators.required(),length(max=5120,min=10)])

class CampaignInfoForm(CampaignForm):
    thumbnail_url = TextField(validators=[validators.required(),length(max=512)])
    description = TextField(validators=[validators.required(),length(max=128,min=10)])
    full_description = TextField(validators=[validators.required(),length(min=10)])
    campaign_title = TextField(validators=[validators.required(),length(max=64,min=5)])
    videos = TextField()
    
    def validate_videos(form, field):
        videos = json.loads(field.data)
        errors = []
        
        for url in videos:
            parsed = urlparse(url)
            #if not ((parsed.hostname == 'youtu.be' and parsed.path) or ((parsed.hostname == 'www.youtube.com' or parsed.hostname == 'youtube.com'))):
            #    errors.append(url)
        
        if errors:
            raise ValidationError(json.dumps(errors))

