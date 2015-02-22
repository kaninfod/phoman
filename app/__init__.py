__author__ = 'martin'
from flask import Flask
from werkzeug.contrib.cache import SimpleCache

#from flask.ext.mongoengine import MongoEngine
from flask.ext.pymongo import PyMongo

app = Flask(__name__)


#app.config["MONGODB_SETTINGS"] = {'DB': "phoman"}
#app.config["SECRET_KEY"] = "KeepThisS3cr3t"
#db = MongoEngine(app)

from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client['phoman3']




from app import views





