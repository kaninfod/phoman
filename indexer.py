__author__ = 'hingem'
from app.model.image import image
from app import *
import os
import logging
import argparse
from app.model.mongo_db import get_image, save_image, locate_image, get_images

file_list = "file.lst"
file_store = app.config['IMAGE_STORE']




def scan_files():
    hourly_scan = r"""find '""" + file_store + r"""' -newermt $(date +%Y-%m-%d -d '1 year ago') -type f -print > """ + file_list
    os.system(hourly_scan)
    with open(file_list) as f:
        for file_path in f:
            file_path = file_path.strip("\n")
            if os.path.isfile(file_path):
                img = image(file_path)
                logging.info('indexed: %s with exif:%s, and id: %s' % (file_path, img.db_has_exif, img.db_id))





def scan_locations():

    images = get_images({'db_latitude':{"$ne":None}})
    for img in images:
        img_obj = image(img, update_location=True)
        img_obj.set_tags()
        img_obj.__mongo_save__()



def scan_files_mac():
    os.system("")
    path = app.config["IMAGE_STORE"]
    for root, dirnames, filenames in os.walk(path):
        for filename in filenames:
            if os.path.splitext(filename)[1] == ".jpg":
                fn = root + "/" + filename
                logging.info('indexing image file: %s' % filename)
                img = image(fn)
                logging.info('indexed: %s with exif:%s, and id: %s' % (filename, img.db_has_exif, img.db_id))

if __name__ == "__main__":



    parser = argparse.ArgumentParser(description='Process some integers.')

    parser.add_argument('--files', dest='files', action='store_true',
                       help='sum the integers (default: find the max)')

    parser.add_argument('--mac', dest='mac', action='store_true',
                       help='sum the integers (default: find the max)')

    parser.add_argument('--locations', dest='locations', action='store_true',
                       help='sum the integers (default: find the max)')

    args = parser.parse_args()

    if args.files:
        scan_files()
    elif args.locations:
        scan_locations()
    elif args.mac:
        scan_files_mac()

    #logging.basicConfig(format='%(asctime)s %(message)s', filename='image_scan.log',level=logging.DEBUG)
    #do_loop()