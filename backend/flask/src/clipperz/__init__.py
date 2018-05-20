import os

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from simplekv.db.sql import SQLAlchemyStore
from flask_kvsession import KVSessionExtension
from config import *

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_url_path='')
config_name = os.getenv('FLASK_ENV', 'Production')
app.config.from_object(config[config_name])

lm = LoginManager()
lm.init_app(app)

db = SQLAlchemy(app)
store = SQLAlchemyStore(db.engine, db.metadata, 'sessions')
kvsession = KVSessionExtension(store, app)

# Generate a secret random key for the session
app.secret_key = os.urandom(24)

from clipperz import views, models, api
