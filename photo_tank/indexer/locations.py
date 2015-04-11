__author__ = 'hingem'

from photo_tank.model.photo import Photo
from photo_tank.model.Image_helper import *
from photo_tank.app import app


images = app.db.get_images({'location.status':0})

def do_loop():

    for img in images:
        photo = Photo(img)
        ih = ImageHelper(photo.files.original_path)
        ih.lookup_location(photo,photo.location)
        app.db.save_image(photo)

if __name__ == "__main__":


    do_loop()