__author__ = 'hingem'


from app.model.image import image
from app import *
import os
import logging
from app.model.exif_data_handler import get_exif_data, get_lat_lon, lookup_location


images = imagesDB.find({'db_location':False})

for img in images:
    img_obj = image(img, update_location=True)
    img_obj.set_tags()
    img_obj.__mongo_save__()
