from models.campaign import Campaign
from services.database import db


class SocialLink(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    url = db.Column(db.String(256), nullable=False)

    campaign_id = db.Column(db.Integer(),db.ForeignKey(Campaign.id))
    campaign = db.relationship(Campaign,backref='socaillink')