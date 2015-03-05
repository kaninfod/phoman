__author__ = 'martin'
from flask import Flask
from pymongo import MongoClient


app = Flask(__name__)
#app.config.from_object('config')

app.secret_key = 'ldjnfieveioecoecococeockeock'
app.config['IMAGE_STORE'] = "/home/martin/Pictures/000 Master - Auto Backup/2014/"
app.config["IMAGE_THUMBS"] = "/home/martin/Pictures/thumbs/"
client = MongoClient('localhost', 27017)
db = client['phoman3']
imagesDB = db['images']
collectionsDB = db['collections']

ImagePersistedFields = [
    "make",
    "model",
    "dateTaken",
    "year",
    "month",
    "day",
    "ImageUniqueID",
    "path",
    "hasEXIF",
    "size",
    "id"
]
from app import views

