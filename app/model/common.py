__author__ = 'martin'

import os
from . import image

def indexImages(path):

    for root, dirnames, filenames in os.walk(path):
        for filename in filenames:
            fn = root + "/" + filename
            img = image.image(fn)

def findImages():
