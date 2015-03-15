__author__ = 'martin'
from flask import Flask
from pymongo import MongoClient
import logging


app = Flask(__name__)
app.secret_key = 'ldjnfieveioecoecococeockeock'

# Mac
#app.config['IMAGE_STORE'] = "/Users/hingem/my_image_store/"
#app.config["IMAGE_THUMBS"] = "/Users/hingem/thumbs/"
#app.config["LOOKUP_LOCATION"] = True

#asus
app.config['IMAGE_STORE'] = "/home/martin/Pictures/000 Master - Auto Backup/2014 - copied across"
app.config["IMAGE_THUMBS"] = "/home/martin/Pictures/thumbs/"

client = MongoClient('localhost', 27017)
db = client['phoman3']
imagesDB = db['images']
collectionsDB = db['collections']
albumsDB = db['albums']

app.config['DEBUG'] = True

filehandler = logging.FileHandler('phoman.log')
filehandler.setLevel(logging.DEBUG)
# create console handler with a higher log level
consolehandler = logging.StreamHandler()
consolehandler.setLevel(logging.ERROR)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
filehandler.setFormatter(formatter)
consolehandler.setFormatter(formatter)
# add the handlers to the logger
app.logger.addHandler(filehandler)
app.logger.addHandler(consolehandler)

from app import views, model

