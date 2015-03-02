#from models.content import content_likes_table
import uuid
from app import cache
from models import User

from services.database import db_session, db

class UserService:
    @cache.memoize(50)
    def get(self,user_id):
        return db.session.query(User).filter_by(id=user_id).first()

    def get_by_email(self,email):
        return db.session.query(User).filter_by(email=email).first()

    def has_liked_content(self,user_id, content_id):
       pass

    def get_by_api_key(self,api_key):
        return db.session.query(User).filter_by(api_key=api_key).first()

    def get_by_reset_hash(self,reset_hash):
        return db.session.query(User).filter_by(reset_hash=reset_hash).first()

    def get_by_fid(self,fid):
        return db.session.query(User).filter_by(fid=fid).first()


