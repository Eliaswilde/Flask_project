import datetime
from sqlalchemy import Enum
from services.database import db
from sqlalchemy.orm import relationship


class User(db.Model):

    #__tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    icon_url = db.Column(db.String(512))
    api_key = db.Column(db.String(256))
    reset_hash = db.Column(db.String(256))
    user_type = db.Column(db.Integer, default=0, nullable=False)
    is_verified = db.Column(db.Boolean(), default=False, nullable=False)
    is_user_active = db.Column('is_active',db.Boolean(), default=True, nullable=False)
    birth_date = db.Column(db.DateTime)
    date = db.Column(db.DateTime,default=datetime.datetime.now())
    phone = db.Column(db.String(32))
    is_anonymous = db.Column(db.Boolean(), default=False, nullable=False)

    avatar = db.Column(db.String(512),default='http://res.cloudinary.com/hzdmrhkl4/image/upload/v1399526643/yf6s7buokuqcubtiiyjb.png')

    company_name = db.Column(db.String(100), nullable=True)
    title = db.Column(db.String(100), nullable=True)
    bio = db.Column(db.String(500), nullable=True)

    fb_profile = db.Column(db.String(200), nullable=True)
    linkedin_profile = db.Column(db.String(200), nullable=True)
    twitter_profile = db.Column(db.String(200), nullable=True)
    youtube_profile = db.Column(db.String(200), nullable=True)
    imdb_profile = db.Column(db.String(200), nullable=True)
    website_profile = db.Column(db.String(200), nullable=True)

    shipping_info_id = db.Column(db.ForeignKey('contact_info.id'))
    shipping_info = relationship('ContactInfo',
                                 foreign_keys=[shipping_info_id],
                                 cascade='all,delete', backref='shipping_user')

    billing_info_id = db.Column(db.ForeignKey('contact_info.id'))
    billing_info = relationship('ContactInfo',
                                foreign_keys=[billing_info_id],
                                cascade='all,delete', backref='billing_user')

    notif_featured_newsletter = db.Column(db.Boolean(), default=False)
    notif_partner_events = db.Column(db.Boolean(), default=False)
    notif_sneak_peeks = db.Column(db.Boolean(), default=False)
    notif_project_updates = db.Column(db.Boolean(), default=False)
    notif_backer_summary = db.Column(db.Boolean(), default=False)
    notif_comments = db.Column(db.Boolean(), default=False)
    notif_follower_summary = db.Column(db.Boolean(), default=False)

    campaigns = db.relationship('Campaign', backref='user', lazy='dynamic')
    comments = db.relationship('Comment', backref='user', lazy='dynamic')

    @property
    def is_admin(self):
        return self.user_type == UserType.Admin

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def get_user_type(self):
        return UserType(self.user_type)

    # Required for administrative interface
    def __str__(self):
        return self.username

    @property
    def serialize(self):
        return {
            'id'        : self.id,
            'first_name': unicode(self.first_name),
            'last_name': unicode(self.last_name),
            'username': unicode(self.username),
            'icon_url': unicode(self.icon_url),
            'is_active': unicode(self.is_active),
            'api_key': unicode(self.api_key),
        }

    @property
    def serialize_light(self):
        return {
            'id'        : self.id,
            'first_name': unicode(self.first_name),
            'last_name': unicode(self.last_name),
            'username': unicode(self.username),
            'icon_url': unicode(self.icon_url),
            'is_active': unicode(self.is_active),
            'api_key': unicode(self.api_key),
        }


class UserType(Enum):
    Backer = 0
    Producer = 1
    Admin = 2
