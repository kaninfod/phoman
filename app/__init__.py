__author__ = 'martin'
from flask import Flask
from pymongo import MongoClient


app = Flask(__name__)


client = MongoClient('localhost', 27017)
db = client['phoman3']

from app import views





