__author__ = 'martin'
import logging

from flask import Flask


app = Flask(__name__)
app.config.from_pyfile('../phototank.conf')


filehandler = logging.FileHandler(app.config["LOG_PATH"])
filehandler.setLevel(app.config["LOG_LEVEL"])
# create console handler with a higher log level
consolehandler = logging.StreamHandler()
consolehandler.setLevel(app.config["LOG_LEVEL"])
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
filehandler.setFormatter(formatter)
consolehandler.setFormatter(formatter)
# add the handlers to the logger
app.logger.addHandler(filehandler)
app.logger.addHandler(consolehandler)




from photo_tank.app import views
from photo_tank.model import database

