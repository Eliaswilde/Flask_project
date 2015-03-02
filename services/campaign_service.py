#from models.content import content_likes_table
import uuid
from models import Campaign
from models.user import UserType
from services.database.database import mongodb, db


class CampaignService:
    def get_draft(self,draft_id):
        return mongodb.campaign_draft.find_one({"draft_id":draft_id})

    def add_draft(self,user_id,draft_id,data):
        mongodb.campaign_draft.insert({ "user_id" : user_id, "draft_id" : draft_id, "data" : data })

    def create_campaign(self,user_id,draft_id,name):
        c = Campaign(
            title=name,
            draft_id=draft_id,
            user_id=user_id
        )
        db.session.add(c)
        db.session.commit()
        return c

    def save_draft(self,user_id,draft_id,data):
        draft = mongodb.campaign_draft.find_one({"draft_id":draft_id})
        if(draft != None):
            mongodb.campaign_draft.remove({"_id": draft["_id"]})
        mongodb.campaign_draft.insert({ "user_id" : user_id, "draft_id" : draft_id, "data" : data })




