import datetime
from sqlalchemy import Enum
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.orm import relationship
from services.database import db
from models.campaign import Campaign, Reward
from models.user import User

__author__ = 'rporter'



class Order(db.Model):
    id = db.Column(UUID(as_uuid=True), default=lambda: uuid.uuid4(), primary_key=True)
    cost = db.Column(db.Float, default=0, nullable=False)
    contribution = db.Column(db.Float, default=0, nullable=False)
    tax = db.Column(db.Float, default=0, nullable=False)
    shipping = db.Column(db.Float, default=0, nullable=False)
    total = db.Column(db.Float, default=0, nullable=False)

    order_status_id = db.Column(db.Integer, nullable=False)

    is_shipping = db.Column(db.Boolean())
    is_private = db.Column(db.Boolean())

    shipping_info_id = db.Column(db.ForeignKey('contact_info.id'))
    shipping_info = db.relationship('ContactInfo',
                                 foreign_keys=[shipping_info_id],
                                 cascade='all,delete', backref='shipping_order')

    billing_info_id = db.Column(db.ForeignKey('contact_info.id'))
    billing_info = db.relationship('ContactInfo',
                                foreign_keys=[billing_info_id],
                                cascade='all,delete', backref='billing_order')

    shipping_date = db.Column(db.DateTime)

    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    user = db.relationship('User')

    reward_id = db.Column(UUID(as_uuid=True), db.ForeignKey(Reward.id))
    reward = db.relationship('Reward')

    campaign_id = db.Column(db.Integer, db.ForeignKey(Campaign.id), nullable=False)
    campaign = db.relationship('Campaign')

    created_date = db.Column(db.DateTime,default=datetime.datetime.now())

    paypal_order_id = db.Column(db.String(128), nullable=False)


class OrderStatus(Enum):
    Created = 0
    Submitted = 1
    Failed = 2
    Success = 3
    Canceled = 4
