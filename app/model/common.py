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


def getCollections():
    return db['collections'].find()

