# Create models

from services.database import db
from models import User
from models.campaign import Campaign


class Comment(db.Model):

    #__tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(256), nullable=False)
    date = db.Column(db.DateTime, nullable=True)
    is_private = db.Column(db.Boolean())
    is_active = db.Column(db.Boolean(), default=False, nullable=False)
    is_hidden = db.Column(db.Boolean(), default=False, nullable=False)
    is_shown_by_campaign_owner = db.Column(db.Boolean(), default=False, nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey(User.id), nullable=False)
    campaign_id = db.Column(db.Integer(), db.ForeignKey(Campaign.id), nullable=False)

    # Required for administrative interface
    def __str__(self):
        return self.text

