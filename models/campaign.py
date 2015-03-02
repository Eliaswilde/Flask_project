import datetime
from sqlalchemy.dialects.postgresql import UUID
import uuid
from config import FANBACKED_BASE_FEE, FANBACKED_EVERGREEN_COST, FANBACKED_FULFILLMENT, FANBACKED_CAMPAIGN_MANAGEMENT
from models import User
from services.database import db






class Campaign(db.Model):

    #__tablename__ = 'campaigns'

    id = db.Column(db.Integer, primary_key=True)
    draft_id = db.Column(db.String(256))
    published_document_id = db.Column(db.String(256))
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    short_vanity_url = db.Column(db.String(64))
    google_analytics = db.Column(db.String(64))
    vanity_url = db.Column(db.String(256))
    thumbnail_url = db.Column(db.String(512))
    confirmation_message = db.Column(db.String(2048))
    created_date = db.Column(db.DateTime)
    campaign_status_id = db.Column(db.Integer)
    is_active = db.Column(db.Boolean(), default=False, nullable=False)

    #form_campaign_info
    short_description = db.Column(db.String(256))
    description = db.Column(db.Text())
    title = db.Column(db.String(256), nullable=False)

    #form_basics
    campaign_receiver_id = db.Column(db.Integer)
    campaign_type_id = db.Column(db.Integer)
    category_id = db.Column(db.Integer)
    expiration_date = db.Column(db.DateTime)
    funding_goal = db.Column(db.Float, default=0)
    funded = db.Column(db.Float, default=0)
    campaign_management = db.Column(db.Boolean(), default=False)
    fulfillment_service = db.Column(db.Boolean(), default=False)
    evergreen_campaign_page = db.Column(db.Boolean(), default=False)

    rewards = db.relationship('Reward',lazy='dynamic',primaryjoin="and_(Reward.campaign_id==Campaign.id,Reward.referrals_needed==0)")
    updates = db.relationship('CampaignUpdate', lazy='dynamic', backref='campaign')
    comments = db.relationship('Comment', backref='campaign', lazy='dynamic')

    campaign_fee_override_id = db.Column(UUID(as_uuid=True), db.ForeignKey('campaign_fee_override.id', use_alter=True,name="fk_campaign_fee_override"), nullable=True)
    campaign_fee_override = db.relationship('CampaignFeeOverride', foreign_keys=[campaign_fee_override_id],primaryjoin="CampaignFeeOverride.id==Campaign.campaign_fee_override_id",post_update=True)

    bonus_reward_id = db.Column(UUID(as_uuid=True), db.ForeignKey('reward.id', use_alter=True,name="fk_bonus_reward"), nullable=True)
    bonus_reward = db.relationship('Reward', foreign_keys=[bonus_reward_id],primaryjoin="Reward.id==Campaign.bonus_reward_id",post_update=True)

    orders = db.relationship('Order',lazy='dynamic')

    active_updates = db.relationship('CampaignUpdate',lazy='dynamic',primaryjoin="and_(CampaignUpdate.campaign_id==Campaign.id,CampaignUpdate.is_active==True)")

    #backers = db.relationship('User',secondary="join(Campaign, User, Campaign.user_id == User.id)",primaryjoin="and_(Order.campaign_id==Campaign.id,Order.order_status_id==3)",secondaryjoin="User.id==Campaign.user_id")

    def __str__(self):
        return self.title

    @property
    def days_left(self):
        return (self.expiration_date-datetime.datetime.now()).days

    @property
    def percent_funded(self):
        return '{0:.2g}'.format((self.funded/self.funding_goal)*100 if self.funded > 0 else 0)

    @property
    def total_fee_percent(self):
        total = 0.0
        if self.campaign_fee_override:
            total += self.campaign_fee_override.base_fee
            total += self.campaign_fee_override.evergreen_cost if self.evergreen_campaign_page else 0.0
            total += self.campaign_fee_override.fulfillment if self.fulfillment_service else 0.0
            total += self.campaign_fee_override.campaign_management if self.campaign_management else 0.0
        else:
            total += FANBACKED_BASE_FEE
            total += FANBACKED_EVERGREEN_COST if self.evergreen_campaign_page else 0.0
            total += FANBACKED_FULFILLMENT if self.fulfillment_service else 0.0
            total += FANBACKED_CAMPAIGN_MANAGEMENT if self.campaign_management else 0.0

        return total



class CampaignUpdate(db.Model):
    id = db.Column(UUID(as_uuid=True), default=lambda: uuid.uuid4(), primary_key=True)
    text = db.Column(db.String(5120), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    user = db.relationship('User')

    campaign_id = db.Column(db.Integer, db.ForeignKey(Campaign.id), nullable=False)

    is_active = db.Column(db.Boolean(), default=True, nullable=False)

    is_exclusive = db.Column(db.Boolean(), default=False, nullable=False)

    created_date = db.Column(db.DateTime, default=datetime.datetime.now())

class Reward(db.Model):
    id = db.Column(UUID(as_uuid=True), default=lambda: uuid.uuid4(), primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    description = db.Column(db.String(2048), nullable=False)
    thumbnail_url = db.Column(db.String(512))
    is_active = db.Column(db.Boolean(), default=False, nullable=False)
    is_available = db.Column(db.Boolean(), default=False, nullable=False)
    cost = db.Column(db.Float, default=0, nullable=False)
    expiration_date = db.Column(db.DateTime)
    delivery_date = db.Column(db.DateTime)
    inventory = db.Column(db.Integer, nullable=False)
    claimed = db.Column(db.Integer, nullable=False)
    is_shipping_required = db.Column(db.Boolean(),nullable=False)
    shipping_fee = db.Column(db.Float, default=0, nullable=False)
    international_shipping_fee = db.Column(db.Float, default=0, nullable=False)
    is_limited_quantity = db.Column(db.Boolean(),nullable=False)
    is_featured = db.Column(db.Boolean(),nullable=False,default=False)
    ordinal = db.Column(db.Integer, nullable=False, default=0)
    referrals_needed = db.Column(db.Integer,default=0, nullable=False)

    campaign_id = db.Column(db.Integer, db.ForeignKey(Campaign.id), nullable=False)
    campaign = db.relationship('Campaign',primaryjoin="Campaign.id==Reward.campaign_id")


class CampaignFeeOverride(db.Model):
    id = db.Column(UUID(as_uuid=True), default=lambda: uuid.uuid4(), primary_key=True)
    base_fee = db.Column(db.Float, default=0, nullable=False)
    evergreen_cost = db.Column(db.Float, default=0, nullable=False)
    campaign_management = db.Column(db.Float, default=0, nullable=False)
    fulfillment = db.Column(db.Float, default=0, nullable=False)
    first_money_threshold = db.Column(db.Float, default=0, nullable=False)

    campaign_id = db.Column(db.Integer, db.ForeignKey(Campaign.id), nullable=False)
    campaign = db.relationship('Campaign',primaryjoin="Campaign.id==CampaignFeeOverride.campaign_id")
