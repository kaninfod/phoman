__author__ = 'martin'
from flask import Flask
import logging

app = Flask(__name__)
app.config.from_pyfile('../phoman.conf')


filehandler = logging.FileHandler(app.config["LOG_PATH"])
filehandler.setLevel(logging.DEBUG)
# create console handler with a higher log level
consolehandler = logging.StreamHandler()
consolehandler.setLevel(logging.DEBUG)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
filehandler.setFormatter(formatter)
consolehandler.setFormatter(formatter)
# add the handlers to the logger
app.logger.addHandler(filehandler)
app.logger.addHandler(consolehandler)




from app import views, model

