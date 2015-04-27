__author__ = 'martin'

import logging
from photo_tank.model.database import Database

from flask import Flask
app = Flask(__name__)
app.config.from_pyfile('../conf/phototank.conf')

DB_PORT = app.config["DB_PORT"]
DB_HOST = app.config["DB_HOST"]
DB_NAME = app.config["DB_NAME"]
app.db = Database(port=DB_PORT, host=DB_HOST, db_name=DB_NAME)
#app.db.initialize_db()

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



