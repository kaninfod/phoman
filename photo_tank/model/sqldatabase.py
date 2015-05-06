__author__ = 'hingem'

from peewee import *
from photo_tank.app import sqldb

class Photo(sqldb.Model):
    date_taken = DateTimeField()
