import datetime
import uuid
from bson import json_util
from flask import url_for, request, json, jsonify, abort
from flask.ext.admin import form
from flask.ext import admin, login
from flask.ext import login
from flask.ext.admin.contrib import sqla
from flask_admin.model.helpers import get_mdict_item_or_list

from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url

from markupsafe import Markup
import time
from sqlalchemy import func
from wtforms import SelectField
from app import Cloudinary, cloudinary
from app.console.admin.BCModelView import BCModelView
from app.console.admin.fields.fields import BCDateField
from app.console.admin.forms.campaigncreateform import CampaignBasicForm, CampaignInfoForm, CampaignPaidForm, CampaignRewardForm, CampaignBonusRewardForm, CampaignConfirmationMessageForm
from helpers.urlify import urlify
from models import Campaign, Reward
from models.user import UserType
from services.campaign_service import CampaignService
from werkzeug.utils import redirect
from services.database import db
from services.database.database import mongodb
from services.stats_service import get_visits_daily

campaign_service = CampaignService()
class CampaignView(BCModelView):
    create_template = 'shared/create_campaign.html'
    edit_template = 'shared/create_campaign.html'

    def get_query(self):
        return self.session.query(self.model).filter_by(user_id=login.current_user.id)

    def get_count_query(self):
        return self.session.query(func.count('*')).select_from(self.model).filter_by(user_id=login.current_user.id)


    def _list_thumb_thumbnail(view, context, model, name):
        return Markup('<img width="100" src="%s">' % model.thumbnail_url)

    def _campaign_view(view, context, model, name):
        return Markup('<a href="/c/%s/">View</a>' % model.vanity_url)

    def _campaign_status(view, context, model, name):
        if(model.campaign_status_id == None):
            return 'None'
        choices=[(0, 'Draf'), (1, 'influencer'), (2, 'specialist'), (3, 'admin')]
        return choices[model.campaign_status_id][1]

    def _campaign_type(view, context, model, name):
        if(model.campaign_type_id == None):
            return 'None'
        choices=[
                    (1, 'Flexible Goal'),
                    (2, 'Fixed Goal'),
                    (3, 'No Goal'),
                ]
        print model.campaign_type_id
        return choices[model.campaign_type_id-1][1]

    column_formatters = {
        'thumbnail_url': _list_thumb_thumbnail,
        'status':_campaign_status,
        'type':_campaign_type,
        'view':_campaign_view
    }

    column_list = ('id', 'thumbnail_url', 'title','status','type','funded','funding_goal','view')

    @admin.expose('/create/', methods=('GET','POST'))
    def create_view(self):
        draft_id = request.args.get('draft_id')
        if draft_id == None:
            draft_id = str(uuid.uuid4())
            c = campaign_service.create_campaign(login.current_user.id,draft_id,"Draft "+time.strftime("%d/%m/%Y %I:%M:%S"))
            return redirect(url_for('.edit_view')+"?draft_id="+draft_id+"&id="+str(c.id))
        else:
            form_data = campaign_service.get_draft(draft_id)
            form_output = form_data["data"] if form_data != None else {}
            self._template_args['form_data'] = json_util.dumps(form_output)

        self._template_args['draft_id'] = draft_id
        return super(CampaignView, self).create_view()





    @admin.expose('/edit/', methods=('GET','POST'))
    def edit_view(self):

        id = get_mdict_item_or_list(request.args, 'id')
        model = self.get_one(id)

        if not self.has_campaign_access(model):
            abort(404)

        draft_id = model.draft_id

        self._template_args['draft_id'] = draft_id
        form_data = campaign_service.get_draft(draft_id)
        form_output = form_data["data"] if form_data != None else {}
        self._template_args['form_data'] = json_util.dumps(form_output)
        return super(CampaignView, self).edit_view()

    def validate_campaign(self,json_data):
        def validate_form(form,name):
                form.csrf_enabled=False
                form.validate()
                return { "form" : name, "errors" : [{ "name" : k, "errors" : [str(inner_v) for inner_v in v] } for k, v in form.errors.items()]}

        form_errors = []
        
        # Serialize vidoes list before passing to the form
        campaign_info_data =  json_data['form_campaign_info'].copy()
        campaign_info_data['videos'] = json.dumps(campaign_info_data['videos'])
        
        form_errors.append(validate_form(CampaignInfoForm.from_json(campaign_info_data),"form_campaign_info"))
        form_errors.append(validate_form(CampaignBasicForm.from_json(json_data["form_basics"]),"form_basics"))
        form_errors.append(validate_form(CampaignPaidForm.from_json(json_data["form_paid"]),"form_paid"))#
        form_errors.append(validate_form(CampaignBonusRewardForm.from_json(json_data["form_bonus_reward"]),"form_bonus_reward"))
        form_errors.append(validate_form(CampaignConfirmationMessageForm.from_json(json_data["form_confirmation_message"]),"form_confirmation_message"))


        reward_form_errors = []
        for reward_forms in json_data["form_rewards"]:
            error_data = validate_form(CampaignRewardForm.from_json(reward_forms),"form_rewards");
            error_data["id"] = reward_forms["id"]
            reward_form_errors.append(error_data)

        form_errors.append({"form":"form_rewards","errors":reward_form_errors})

        return form_errors

    def save_draft_to_campaign(self,campaign,draft_data):

        form_campaign_info = CampaignInfoForm.from_json(draft_data["form_campaign_info"])
        form_basics = CampaignBasicForm.from_json(draft_data["form_basics"])
        form_paid = CampaignPaidForm.from_json(draft_data["form_paid"])
        form_bonus_reward = CampaignBonusRewardForm.from_json(draft_data["form_bonus_reward"])
        form_confirmation_message = CampaignConfirmationMessageForm.from_json(draft_data["form_confirmation_message"])

        campaign.campaign_type_id = form_basics.campaign_type_id.data
        campaign.category_id = form_basics.category_id.data
        campaign.campaign_receiver_id = form_basics.campaign_receiver_id.data
        campaign.funding_goal = float(str(form_basics.dollar_amount.data))
        campaign.expiration_date = form_basics.deadline.data
        campaign.fulfillment_service = form_basics.fulfillment_service.data
        campaign.evergreen_campaign_page = form_basics.evergreen_campaign_page.data
        campaign.fulfillment_service = form_basics.fulfillment_service.data
        campaign.campaign_management = form_basics.campaign_management.data

        campaign.description = form_campaign_info.full_description.data
        campaign.short_description = form_campaign_info.description.data
        campaign.title = form_campaign_info.campaign_title.data
        campaign.thumbnail_url = form_campaign_info.thumbnail_url.data

        campaign.confirmation_message = form_confirmation_message.confirmation_message.data

        campaign.vanity_url = urlify(campaign.title)

        for i_reward in campaign.rewards:
            i_reward.is_active=False

        for idx, reward_forms in enumerate(draft_data["form_rewards"]):
            form_reward = CampaignRewardForm.from_json(reward_forms);
            current_reward = None
            for i_reward in campaign.rewards:
                if str(i_reward.id).lower() == str(form_reward.id.data).lower():
                    current_reward = i_reward
                    i_reward.is_active=True
                    break

            if current_reward != None:
                pass
            else:
                current_reward = Reward()
                current_reward.claimed = 0
                current_reward.id = form_reward.id.data
                campaign.rewards.append(current_reward)

            current_reward.ordinal = idx
            current_reward.is_featured = form_reward.is_featured.data
            current_reward.title = form_reward.name.data
            current_reward.inventory = form_reward.quantity.data if form_reward.quantity.data else 0
            current_reward.cost = form_reward.dollar_amount.data
            current_reward.thumbnail_url = form_reward.thumbnail_url.data
            current_reward.description = form_reward.description.data
            current_reward.delivery_date = form_reward.delivery_date.data
            current_reward.is_shipping_required = form_reward.shipping_required.data
            current_reward.is_limited_quantity = form_reward.limited_quantity.data
            current_reward.international_shipping_fee = form_reward.international_shipping_fee.data if form_reward.international_shipping_fee.data else 0
            current_reward.shipping_fee = form_reward.shipping_fee.data if form_reward.shipping_fee.data else 0


            if campaign.bonus_reward == None:
                campaign.bonus_reward = Reward()
                campaign.bonus_reward.campaign = campaign

            campaign.bonus_reward.claimed = 0
            campaign.bonus_reward.referrals_needed = form_bonus_reward.referrals_needed.data
            campaign.bonus_reward.title = form_bonus_reward.name.data
            campaign.bonus_reward.inventory = form_bonus_reward.quantity.data if form_bonus_reward.quantity.data else 0
            campaign.bonus_reward.cost = 0
            campaign.bonus_reward.thumbnail_url = form_bonus_reward.thumbnail_url.data
            campaign.bonus_reward.description = form_bonus_reward.description.data
            campaign.bonus_reward.delivery_date = form_bonus_reward.delivery_date.data
            campaign.bonus_reward.is_shipping_required = form_bonus_reward.shipping_required.data
            campaign.bonus_reward.is_limited_quantity = form_bonus_reward.limited_quantity.data
            campaign.bonus_reward.international_shipping_fee = form_bonus_reward.international_shipping_fee.data if form_bonus_reward.international_shipping_fee.data else 0
            campaign.bonus_reward.shipping_fee = form_bonus_reward.shipping_fee.data if form_bonus_reward.shipping_fee.data else 0

        return campaign

    @admin.expose('/save_draft/', methods=('GET','POST'))
    def save_draft(self):
        if request.method == 'POST':

            c_id = int(request.form['campaign_id'])
            draft_id = str(request.form['draft_id'])

            model = self.get_one(c_id)

            if not self.has_campaign_access(model):
                abort(404)

            if model.draft_id != draft_id:
                return jsonify({"reload" : True})

            json_data = json.loads(request.form['data'])
            form_errors = self.validate_campaign(json_data)
            

            campaign_service.save_draft(login.current_user.id,str(json_data['draft_id']),json_data)

            return jsonify({ "errors" : form_errors})
        abort(404)


    @admin.expose('/publish/', methods=('GET','POST'))
    def publish(self):
        if request.method == 'POST':

            draft_id = request.form['draft_id']
            campaign_id = request.form['campaign_id']

            json_data = campaign_service.get_draft(draft_id)['data']
            form_errors = self.validate_campaign(json_data)

            model = self.get_one(campaign_id)

            if not self.has_campaign_access(model):
                abort(404)

            if model.draft_id != draft_id:
                 return redirect(url_for('.index_view'))

            campaign_service.save_draft(login.current_user.id,str(json_data['draft_id']),json_data)

            has_errors = False
            for _form in form_errors:
                if(_form["form"] == "form_rewards"):
                    for inner_error in _form["errors"]:
                        if(len(inner_error["errors"]) > 0):
                            has_errors = True
                elif(len(_form["errors"]) > 0):
                    has_errors = True

            if has_errors:
                return redirect(url_for('.edit_view')+"?draft_id="+draft_id+"&id="+str(campaign_id))
            else:
                model = self.save_draft_to_campaign(model,json_data)
                new_draft_id = str(uuid.uuid4())
                model.draft_id = new_draft_id
                campaign_service.add_draft(login.current_user.id,str(new_draft_id),json_data)
                model.published_document_id = str(uuid.uuid4())
                campaign_service.add_draft(login.current_user.id,str(model.published_document_id),json_data)
                db.session.commit()
                return redirect(url_for('.index_view'))
        abort(404)


    @admin.expose('/upload/', methods=('POST', 'GET'))
    def upload(self):
        if request.method == 'POST':
            file = request.files['Filedata']
            if file:
                upload_result = cloudinary.upload_image(file)
                return jsonify({'status': 'ok', 'image': upload_result["url"]})

        return jsonify({'status': 'ok', 'avatar': ''})

    @admin.expose('/save_as_draft/', methods=('GET','POST'))
    def save_as_draft(self):
        if request.method == 'POST':
            draft_id = request.form['draft_id']
            campaign_id = request.form['campaign_id']
            model = self.get_one(campaign_id)
            if not self.has_campaign_access(model):
                abort(404)

            data = request.form['data']
            campaign_service.save_draft(login.current_user.id,draft_id,json.loads(data))
        return ''


    def has_campaign_access(self,campaign):
        if login.current_user.user_type == UserType.Admin:
            return True
        elif login.current_user.id == campaign.user_id:
            return True
        else:
            return False

   # form_overrides = {
    #    'path': form.ImageUploadField
   # }
    # Alternative way to contribute field is to override it completely.
    # In this case, Flask-Admin won't attempt to merge various parameters for the field.

