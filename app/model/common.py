__author__ = 'martin'

import os
from app.model.image import image
from app.model.imageCollection import imageCollection
from app import db

def indexImages(path):

    for root, dirnames, filenames in os.walk(path):
        for filename in filenames:
            fn = root + "/" + filename
            img = image(fn)

def findImages():
    imgcol = imageCollection()
    print()


def populateCollection(collection):
    image_db = db['images']

    k = image_db.find(collection.query)
    for ima in k:
        l = image(ima)
        collection[l.id] = l
    return collection
