__author__ = 'martin'
from flask import Flask
from werkzeug.contrib.cache import SimpleCache

from flask.ext.mongoengine import MongoEngine


app = Flask(__name__)

app.config["MONGODB_SETTINGS"] = {'DB': "phoman"}
app.config["SECRET_KEY"] = "KeepThisS3cr3t"
db = MongoEngine(app)

cache = SimpleCache()

from app import views, model
from app.model import image




