# Create models

from services.database import db
from models.user import User


class Funder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    description = db.Column(db.String(512), nullable=False)
    date = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean(), default=False, nullable=False)
    amount = db.Column(db.Float)
    is_active = db.Column(db.Boolean())
    user_id = db.Column(db.Integer(), db.ForeignKey(User.id))
    user = db.relationship(User, backref='comment')
    is_private = db.Column(db.Boolean())


    # Required for administrative interface
    def __str__(self):
        return self.amount

