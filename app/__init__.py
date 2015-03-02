import locale
from flask import (Flask, render_template)
from flask_admin.contrib.sqla import ModelView
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask.ext import admin, login
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.cache import Cache
from micawber import bootstrap_basic, Provider
from micawber.contrib.mcflask import add_oembed_filters
from app.campaign.views import campaign
from app.campaign.forms import LoginForm, SignupForm
from app.console.account.ContributionsView import ContributionsView
from app.console.admin.BCModelView import BCModelView

from app.console.views import console
from app.www.views import www
from models import User, Campaign, Order
from models.campaign import CampaignFeeOverride, Reward
from services.database import db, db_session
import wtforms_json
from cloudinary import uploader
import os
from app.sessions import MongoSessionInterface
from config import MONGOHQ_URL

class Cloudinary(object):
  def __init__(self, app):
    config = app.config['CLOUDINARY_URL'].split('://')[1]
    config = config.replace("@", ":")
    self.api_key, self.api_secret, self.name = config.split(":")

  def upload_image(self, image):
    keys = {'public_id': 1001}
    res = uploader.upload(image,  api_key=self.api_key,
      api_secret=self.api_secret,
      cloud_name=self.name)
    return res


def create_app():
    app = Flask("backercapital")
    app.session_interface = MongoSessionInterface(MONGOHQ_URL)
    app.config['DEBUG'] = True
    app.config['SQLALCHEMY_ECHO'] = True

    app.config['SECRET_KEY'] = '123456790'

    db = SQLAlchemy(app)
    app.register_blueprint(campaign)
    app.register_blueprint(console)
    app.register_blueprint(www)
    #app.before_request(assign_transaction_id)
    app.teardown_appcontext(shutdown_session)

    return app


def shutdown_session(response):
	db.session.remove()
	return response



app = create_app()
app.config.from_object('config')
mail = Mail(app)
cloudinary = Cloudinary(app)
cache = Cache(app)
wtforms_json.init()
bcrypt = Bcrypt()
oembed_providers = bootstrap_basic()
oembed_providers.register('http://www.ustream.tv/channel/\S+', Provider('http://www.ustream.tv/oembed'))
add_oembed_filters(app, oembed_providers)


from services.user_service import UserService

user_service = UserService()



login_manager = LoginManager()

#login_manager.anonymous_user = Anonymous
login_manager.login_view = "login"
login_manager.login_message = u"Please log in to access this page."
login_manager.refresh_view = "reauth"


import paypalrestsdk
paypalrestsdk.configure({
  'mode': 'sandbox',
  'client_id': 'AVbadxCku7MP8IDinubyeLRKbKm3IVOxDf-fkNpZIq7HZlMpSjMAnOSyTlHh',
  'client_secret': 'EDlAKhDBDMc--QGKP5tMts1gj1j5ExpEshPPfV1S36UDBFiw8JV37UULN4Eq'
})

def init_login():
    login_manager = login.LoginManager()
    login_manager.init_app(app)

    # Create user loader function
    @login_manager.user_loader
    def load_user(user_id):
        return user_service.get(int(user_id))


init_login()

locale.setlocale( locale.LC_ALL, '' )
@app.template_filter('to_usd')
def to_usd_filter(s):
    return locale.currency( s, grouping=True).split('.')[0]

@app.template_filter('to_usd')
def to_usd_filter(s):
    return locale.currency( s, grouping=True).split('.')[0]


# Custom Error Handle
@app.errorhandler(404)
def page_404(e):
    login_form = LoginForm()
    signup_form = SignupForm()
    return render_template('shared/404.html', login_form=login_form, signup_form=signup_form), 404

from app.console.account.BackersView import BackersView
from app.console.account.CampaignView import CampaignView
from app.console.account.InboxView import InboxView
from app.console.account.OrderView import OrderView
from app.console.account.ProfileView import ProfileView
from app.console.account.SettingsView import SettingsView
from app.console.admin.BCAdminIndexView import BCAdminIndexView
from app.console.admin.UserView import UserView
from app.console.account.DashboardView import DashboardView
from app.console.admin.CampaignFeeOverrideView import CampaignFeeOverrideView


console = admin.Admin(app, 'admin', index_view=BCAdminIndexView(url='/admin', endpoint='admin',name ='Dashboard'),base_template = 'bc_admin/base.html', )
console.add_view(UserView(User, db_session))
console.add_view(CampaignFeeOverrideView(CampaignFeeOverride, db_session, name='Fee Override'))

admin_account = admin.Admin(app, 'account', index_view=DashboardView( url='/account', endpoint='account',name ='Dashboard'),base_template = 'bc_admin/base.html',)
admin_account.add_view(ProfileView(endpoint ='profileview', name='Profile'))
admin_account.add_view(InboxView(endpoint ='inboxview', name='Inbox'))
admin_account.add_view(CampaignView(Campaign, db_session))
admin_account.add_view(ContributionsView(Order, db_session,endpoint ='contributionview', name='Contribution'))
admin_account.add_view(BackersView(Order, db_session,endpoint ='backersview', name='Backers'))
admin_account.add_view(SettingsView(endpoint ='settingsview', name='Settings'))

admin_backer = admin.Admin(app, 'profile', index_view=BCAdminIndexView( url='/profile', endpoint='profile',name ='Dashboard'),base_template = 'bc_admin/base.html',)
admin_backer.add_view(ProfileView(endpoint ='backerview', name='Profile'))
admin_backer.add_view(InboxView(endpoint ='backerbox', name='Inbox'))
admin_backer.add_view(ContributionsView(Order, db_session,endpoint ='backerbutions', name='Contribution'))
admin_backer.add_view(SettingsView(endpoint ='backersettings', name='Settings'))