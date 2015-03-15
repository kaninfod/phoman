__author__ = 'hingem'
from app.model.image import image
from app import *
import os
import logging





def do_loop():

    path = app.config["IMAGE_STORE"]
    for root, dirnames, filenames in os.walk(path):
        for filename in filenames:
            if os.path.splitext(filename)[1] == ".jpg":
                fn = root + "/" + filename
                logging.info('indexing image file: %s' % filename)
                img = image(fn)
                logging.info('indexed: %s with exif:%s, and id: %s' % (filename, img.db_has_exif, img.db_id))

if __name__ == "__main__":

    logging.basicConfig(format='%(asctime)s %(message)s', filename='image_scan.log',level=logging.DEBUG)
    do_loop()