__author__ = 'martin'
from flask import Flask
import logging

app = Flask(__name__)
app.secret_key = 'ldjnfieveioecoecococeockeock'



# Mac
app.config['IMAGE_STORE'] = "/Users/hingem/my_image_store/"
app.config["IMAGE_THUMBS"] = "/Users/hingem/thumbs/"
app.config["LOOKUP_LOCATION"] = True

#asus
#app.config['IMAGE_STORE'] = "/home/martin/Pictures/000 Master - Auto Backup/2014 - copied across"
#app.config["IMAGE_THUMBS"] = "/home/martin/Pictures/thumbs/"


app.config["IMAGE_THUMB"] = (256, 256)
app.config["IMAGE_MEDIUM"] = (600, 800)
app.config["IMAGE_LARGE"] = (1024, 1200)





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

