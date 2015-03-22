__author__ = 'hingem'


from app.model.image import image
from app import *


images = imagesDB.find({'db_location':False})

def do_loop():



    for img in images:
        img_obj = image(img, update_location=True)
        img_obj.set_tags()
        img_obj.__mongo_save__()


if __name__ == "__main__":


    do_loop()