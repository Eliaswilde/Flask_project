import datetime
from random import random, randint
import uuid
from boto.provider import Provider
from flask import json
import micawber
from app import create_app, app, emails
from app.emails import send_password_reset
from models import User, Order, Campaign
from models.user import UserType
from services.campaign_service import CampaignService

from services.database import db
from services.database.database import mongodb
from services.stats_service import  log_visit, get_visits_daily


db.app = app

now = datetime.datetime.utcnow()
start_time = datetime.datetime.utcnow() - datetime.timedelta(days=90)

#cursor1 = mongodb.stats.daily.find({'metadata.date': { '$gte': start_time, '$lte': now },'metadata.site': 'backercapital','metadata.page': 'somesite.png'},{ 'metadata.date': 1, 'daily': 1 },sort=[('metadata.date', 1)])
cursor1 = get_visits_daily(mongodb,start_time,now,1)
for record in cursor1:
    print json.dumps(record['daily'], ensure_ascii=False)
#while start_time < now:
#    log_visit(mongodb,start_time,34,1)
 #   start_time += datetime.timedelta(seconds=randint(15, 600))

#db.create_all()
#providers = micawber.bootstrap_basic()
#providers.register('http://www.ustream.tv/channel/\S+', Provider('http://www.ustream.tv/oembed'))
#print providers.request('http://www.ustream.tv/channel/nasa-msfc')
print 'done'

ted = User(
    first_name='Ted',
    last_name='Campbell',
    username='tcampbell',
    password='123123',
    email='devteam@backercapital.com',
    user_type=UserType.Producer,
    is_verified=True,
    is_user_active=True,
    title="Executive Producer"
)

c = Campaign(
    title = 'test title'
)

#emails.send_reset_password_complete(ted)

#db.create_all()


#u = User(
#    password='123',
#    email='frodo@gmail.com',
#    user_type=UserType.Backer,
#    is_anonymous=True
#)

#db.session.add(u)
#db.session.commit()



