__author__ = 'hingem'

from photo_tank.model import photo


images = imagesDB.find({'location':False})

def do_loop():

    for img in images:
        img_obj = photo(img, update_location=True)
        img_obj.set_tags()
        img_obj.__mongo_save__()


if __name__ == "__main__":


    do_loop()