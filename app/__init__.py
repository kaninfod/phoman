__author__ = 'martin'
from flask import Flask
from pymongo import MongoClient


app = Flask(__name__)
app.config.from_object('config')
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
