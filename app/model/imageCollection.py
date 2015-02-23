__author__ = 'martin'

from app.model.image import image
from app import db

class imageCollection(dict):

    def __init__(self, query):

        self.image_db = db['images']
        self.query = query

        k = self.image_db.find(self.query)
        for ima in k:
            l = image(ima)
            self[l.id] = l

        print()
def test():
    print()