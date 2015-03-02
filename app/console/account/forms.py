from flask.ext.wtf import Form
from wtforms import SelectField

class SelectCampaignForm(Form):
    campaign = SelectField(u'Campaign')
    
    def __init__(self, choices, *args, **kwargs):
        super(SelectCampaignForm, self).__init__(*args, **kwargs)
        self.campaign.choices = choices
