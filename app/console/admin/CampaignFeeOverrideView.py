from random import randint
from flask import url_for, request
from flask.ext.admin import form
from flask.ext import login
from flask.ext.admin.contrib import sqla
from markupsafe import Markup
from sqlalchemy import func
from wtforms import SelectField
from app.console.admin.BCModelView import BCModelView
from app.console.admin.fields.fields import BCDateField
from config import FANBACKED_BASE_FEE
from models import Order, Reward, Campaign


class CampaignFeeOverrideView(BCModelView):

    def after_model_change(self,form, model, is_created):
        model.campaign.campaign_fee_override = model
        self.session.commit()
        super(CampaignFeeOverrideView, self).after_model_change(form, model, is_created)

    def on_model_delete(self,model):
        model.campaign.campaign_fee_override_id = None
        self.session.commit()
        super(CampaignFeeOverrideView, self).on_model_delete(model)

    form_args = dict(
                campaign_management=dict(default=1)
            )

    column_formatters = {
        'reward': lambda v, c, m, p: m.campaign.title,
    }


    column_list = ('campaign', 'base_fee', 'evergreen_cost','campaign_management','fulfillment')

