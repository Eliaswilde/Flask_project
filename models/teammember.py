from models import User
from models.campaign import Campaign
from services.database import db


class TeamMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    description = db.Column(db.String(512), nullable=False)
    is_active = db.Column(db.Boolean(), default=False, nullable=False)
    date = db.Column(db.DateTime)

    user_id = db.Column(db.Integer(), db.ForeignKey(User.id))
    user = db.relationship(User, backref='teammember')

    campaign_id = db.Column(db.Integer(),db.ForeignKey(Campaign.id))
    campaign = db.relationship(Campaign,backref='teammember')