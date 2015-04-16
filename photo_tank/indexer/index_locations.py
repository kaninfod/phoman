__author__ = 'hingem'

from photo_tank.model.photo import Photo
from photo_tank.model.Image_helper import *
from photo_tank.app import app


images = app.db.get_photos({'location.status':0})

def location_watcher():

    for img in images:
        photo = Photo(img)
        ih = ImageHelper(photo.files.original_path)
        ih.lookup_location(photo,photo.location)
        app.db.save_photo(photo)

if __name__ == "__main__":
    location_watcher()