__author__ = 'martin'

from app.model.image import image
from app import db


class imageCollection():

    def __init__(self, query):

        self.image_db = db['images']
        self.query = query
        self.cursor = self.image_db.find(self.query)
        print()

    def __iter__(self):
        return self

    def __next__(self):

        if self.cursor and self.cursor.alive:
            return image(next(self.cursor))
        else:
            raise StopIteration()
