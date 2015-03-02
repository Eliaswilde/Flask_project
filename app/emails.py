import uuid
from flask import render_template, url_for
from flask.ext.mail import Message
from config import APP_BASE_URL, FANBACKED_NOTIFICATIONS_EMAIL
from decorators import async
from services.database import db
from app import mail, app

@async
def send_async_email(msg):
    with app.app_context():
        mail.send(msg)
    
def send_email(subject, sender, recipients, html_body):
    msg = Message(subject, sender = sender, recipients = recipients)
    msg.body = html_body
    msg.html = html_body
    send_async_email(msg)
    #thr = threading.Thread(target = send_async_email, args = [msg])
    #thr.start()

#==============
#producer
#==============
def send_producer_account_created(user):
    with app.app_context():

        profile_url = APP_BASE_URL + '/profile/'
        create_url =   APP_BASE_URL + '/account/campaignview/'
        send_email('Hey %s, Welcome to FanBacked!' % user.first_name,
            FANBACKED_NOTIFICATIONS_EMAIL,
            [user.email],
            render_template("email/producer_user_account_created.html",user=user,profile_url=profile_url,homepage_url=APP_BASE_URL,create_url=create_url))


def send_producer_goal_not_reached(user,campaign):
    with app.app_context():

        login_url = APP_BASE_URL + '/profile/login/'
        send_email('Hey %s, Welcome to FanBacked!' % user.first_name,
            FANBACKED_NOTIFICATIONS_EMAIL,
            [user.email],
            render_template("email/producer_campaign_ended_goal_not_reached.html",user=user,campaign=campaign,login_url=login_url))

#==============
#backer
#==============
def send_backer_account_created(user):
    with app.app_context():

        profile_url = APP_BASE_URL + '/profile/'
        send_email('Hey %s, Welcome to FanBacked!' % user.first_name,
            FANBACKED_NOTIFICATIONS_EMAIL,
            [user.email],
            render_template("email/backer_user_account_created.html",user=user,profile_url=profile_url,homepage_url=APP_BASE_URL))


#==============
#reset password
#==============
def send_reset_password_complete(user):
    with app.app_context():
        send_email('Password Reset!',
            FANBACKED_NOTIFICATIONS_EMAIL,
            [user.email],
            render_template("email/reset_password_complete.html"))

def send_password_reset(user):
    with app.app_context():
        user.reset_hash = str(uuid.uuid1())
        db.session.commit()

        section_url = 'profile'
        if(user.user_type == 1):
            section_url= 'account'
        elif(user.user_type == 2):
            section_url= 'admin'

        reset_url = APP_BASE_URL +section_url+ '/resetpassword/?reset_hash=' + user.reset_hash
        send_email('Password Reset!',
            FANBACKED_NOTIFICATIONS_EMAIL,
            [user.email],
            render_template("reset_password.html", reset_url = reset_url))