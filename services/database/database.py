from flask.ext.sqlalchemy import SQLAlchemy
from urlparse import urlparse
import pymongo
from config import MONGOHQ_URL

db = SQLAlchemy()
db_session = db.session
mongo_conn = pymongo.Connection(MONGOHQ_URL)
mongodb = mongo_conn[urlparse(MONGOHQ_URL).path[1:]]