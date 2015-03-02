import os
basedir = os.path.abspath(os.path.dirname(__file__))
CACHE_TYPE = 'simple'
CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

OPENID_PROVIDERS = [
    { 'name': 'Google', 'url': 'https://www.google.com/accounts/o8/id' },
    { 'name': 'Yahoo', 'url': 'https://me.yahoo.com' },
    { 'name': 'AOL', 'url': 'http://openid.aol.com/<username>' },
    { 'name': 'Flickr', 'url': 'http://www.flickr.com/<username>' },
    { 'name': 'MyOpenID', 'url': 'https://www.myopenid.com' }]
    

# slow database query threshold (in seconds)
DATABASE_QUERY_TIMEOUT = 0.5
CLOUDINARY_URL = 'cloudinary://536883924777141:JqocL79Z3EteD8VBzDvvfO_Ukkc@hzdmrhkl4'
MONGOHQ_URL = 'mongodb://heroku:oY0JwHEuCAbn-zPXyBjzY9MCn51dwW32k3xfZsE7Cb_Y64wDnPFcbiHJS8kSlyXGabP2cYvRIfdmad0sxnSN8g@oceanic.mongohq.com:10008/app23597006'
# email server
MAIL_SERVER = 'smtp.mandrillapp.com' # your mailserver
MAIL_PORT = 587
MAIL_USE_TLS = False
MAIL_USE_SSL = False
MAIL_USERNAME = 'app23597006@heroku.com'
MAIL_PASSWORD = '51nHQ4vmJCh50xunls98xw'

SQLALCHEMY_DATABASE_URI = os.environ.get('HEROKU_POSTGRESQL_COBALT_URL','postgres://epmgpywdjxwyna:i_9MihDwhjuTREFCy3NT_CPn6B@ec2-54-225-101-199.compute-1.amazonaws.com:5432/d69qmj08uhp0aj')
SQLALCHEMY_ECHO = True
SQLALCHEMY_PAGINATE_MAX_RESULT = 10
# administrator list
ADMINS = ['you@example.com']

# pagination
POSTS_PER_PAGE = 50
MAX_SEARCH_RESULTS = 50

# facebook auth
FACEBOOK_APP_ID = os.environ.get('BC_FB_APP_ID','233477886849857')
FACEBOOK_APP_SECRET = os.environ.get('BC_FB_APP_KEY','4f3980b6b1fb70194ad4d6f5762cebe9')

S3_ACCESS_KEY = os.environ.get('S3_ACCESS_KEY','')
S3_ACCESS_SECRET = os.environ.get('S3_SECRET_KEY','')
S3_BUCKET_NAME = 'beta.fanbacked'
S3_MIN_CHUNK_SIZE = 5242880

APP_BASE_URL = os.environ.get('app_base_url', 'http://127.0.0.1:5000')
#SERVER_NAME = os.environ.get('app_base_url', 'http://127.0.0.1:5000')

FANBACKED_NOTIFICATIONS_EMAIL = 'FanBacked Team <notifications@fanbacked.com>'

FANBACKED_CAMPAIGN_MANAGEMENT = 0.03
FANBACKED_FULFILLMENT = 0.075
FANBACKED_BASE_FEE = 0.05
FANBACKED_EVERGREEN_COST = 0.025

PAYPAL_SECURITY_USERID = os.environ.get('BC_PAYPAL_SECURITY_USERID','jb-us-seller_api1.paypal.com')
PAYPAL_SECURITY_PASSWORD = os.environ.get('BC_PAYPAL_SECURITY_PASSWORD','WX4WTU3S8MY44S7F')
PAYPAL_SECURITY_SIGNATURE = os.environ.get('BC_PAYPAL_SECURITY_SIGNATURE','AFcWxV21C7fd0v3bYYYRCpSSRl31A7yDhhsPUU2XhtMoZXsWHFxu-RWy')
PAYPAL_APPLICATION_ID = os.environ.get('BC_PAYPAL_APPLICATION_ID','APP-80W284485P519543T')
PAYPAL_PRIMARY_ACCOUNT_EMAIL = os.environ.get('BC_PAYPAL_PRIMARY_ACCOUNT_EMAIL','platfo_1255612361_per@gmail.com')


try:
    from local_config import *
except:
    pass