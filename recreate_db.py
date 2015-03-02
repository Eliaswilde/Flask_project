from random import randint, choice
import uuid
from sqlalchemy import func
from app import create_app, app
from app.emails import send_password_reset
from models import User, Campaign, Reward, ContactInfo, Order
from models.campaign import CampaignUpdate
from models.user import UserType

from services.database import db


db.app = app

#db.drop_all()
#db.create_all()
ted = User(
    first_name='Ted',
    last_name='Campbell',
    username='tcampbell',
    password='123123',
    email='tcampbell@fanbacked.com',
    user_type=UserType.Producer,
    is_verified=True,
    is_user_active=True,
    title="Executive Producer"
)

db.session.add(ted)

u = User(
    first_name='Admin',
    last_name='Admin',
    username='admin',
    password='admin',
    email='admin@backercapital.com',
    user_type=UserType.Admin,
    is_verified=True,
    is_user_active=True,
    title="CEO"
)
db.session.add(u)
db.session.commit()

def generate_contact(id):
    c = ContactInfo(
        phone_number='310617024%s'%id,
        address='1373 Golden Road',
        city='Los Angeles',
        state='CA',
        postal_code='9006%s'%id,
        country='USA'
    )
    return c




dummy_text = "<p><img width=\"400\" alt=\"\" align=\"left\" src=\"http://res.cloudinary.com/hzdmrhkl4/image/upload/v1398912655/shntgrq6uzhzfni8btzq.png?n=njpgxkmye\">Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>"
funding_goal = randint(100000,150000)
c = Campaign(
    draft_id='81e7197e-f33e-4ebd-8e34-91cda0e57e47',
    user_id=ted.id,
    id=1,
    thumbnail_url='http://res.cloudinary.com/hzdmrhkl4/image/upload/v1398907258/nm11q7fw7kayohkwcljo.png',
    confirmation_message='<p><img alt="">Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>',
    is_active=True,
    short_description="Short Campaign Descriptionhort Campaign Description",
    description=dummy_text,
    title='New Campaign thats really cool!',
    campaign_receiver_id=3,
    campaign_type_id=3,
    category_id=4,
    expiration_date="2014-06-07 00:00:00",
    funding_goal=funding_goal,
    funded=randint(1,funding_goal),
    fulfillment_service=True,
    campaign_management=True,
    evergreen_campaign_page=True,
    vanity_url='vanity_url',
    )

for i in range(6):
    ci = CampaignUpdate(
        id=uuid.uuid4(),
        text=dummy_text,
        user_id=ted.id,
    )
    c.updates.append(ci)

for i in range(6):
    inventory_count = randint(1,500)
    r = Reward(
        id=uuid.uuid4(),
        title='Something Awesome%s'%i,
        description="This is the description and lets see it a little longer then normal.  This is the description and lets see it a little longer then normal.  This is the description and lets see it a little longer then normal.  ",
        thumbnail_url="http://res.cloudinary.com/hzdmrhkl4/image/upload/v1398927057/hs9gf9a9lbvjenzpsomo.jpg",
        is_active=True,
        is_available=True,
        cost=randint(50,500),
        delivery_date="2014-05-22 00:00:00",
        inventory=inventory_count,
        is_limited_quantity=True,
        is_shipping_required=True,
        claimed=randint(1,inventory_count)
        )
    c.rewards.append(r)

db.session.add(c)
db.session.commit()

for i in range(30):
    b = User(
    first_name=str('Joe%s'%i),
    last_name=str('Backer%s'%i),
    username=str('jbacker%s'%i),
    password=str('backer%s'%i),
    email=str('jbacker%s@backercapital.com'%i),
    user_type=UserType.Backer,
    is_verified=True,
    is_user_active=True,
    title=str('Backer%s'%i)
    )
    b.shipping_info = generate_contact(i)
    b.billing_info = generate_contact(i)
    db.session.add(b)
    db.session.commit()

    if randint(1,5) > 2:
        reward = c.rewards[randint(1,c.rewards.count()-1)]
        o = Order(
         campaign=c,
         reward=reward,
         id=uuid.uuid4(),
         user_id=b.id,
         billing_info_id=b.billing_info_id,
         shipping_info_id=b.shipping_info_id,
         cost=reward.cost,
         tax=reward.cost*0.08,
         shipping=2,
         total=reward.cost + (reward.cost*0.08) + 2,
         order_status_id=1,
         is_shipping=True,
         shipping_date='9/5/2014',
         paypal_order_id=''
        )
        db.session.add(o)

db.session.commit()



