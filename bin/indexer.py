__author__ = 'hingem'
import os
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir) 

from app.model.image import image
from app.model.mongo_db import *
from app.model.exif_data_handler import *
from app import *
import os
from shutil import move

import argparse
from app.model.mongo_db import get_images

file_list = "file.lst"
file_store = app.config['IMAGE_STORE']

IMAGE_STORE = app.config["IMAGE_STORE"]
IMAGE_THUMBS = app.config["IMAGE_THUMBS"]
IMAGE_DETENTION = app.config["IMAGE_DETENTION"]
OTHER_FILES = app.config["OTHER_FILES"]
IMAGE_WATCH_FOLDER = app.config["IMAGE_WATCH_FOLDER"]

def scan_files():
    hourly_scan = r"""find '""" + file_store + r"""' -newermt $(date +%Y-%m-%d -d '1 year ago') -type f -print > """ + file_list
    app.logger.debug("before")
    os.system(hourly_scan)
    app.logger.debug("after")
    with open(file_list) as f:
        for file_path in f:
            file_path = file_path.strip("\n")
            if os.path.isfile(file_path):
                app.logger.debug("scanning: %s" % file_path)
                img = image(file_path)






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
                app.logger.debug("scanning: %s" % filename)
                img = image(fn)
                app.logger.debug('indexed: %s with exif:%s, and id: %s' % (filename, img.db_has_exif, img.db_id))


def index_watcher():
    os.system("")
    path = IMAGE_WATCH_FOLDER

    app.logger.info("Indexing of %s initiated" % IMAGE_WATCH_FOLDER)
    for root, dirnames, filenames in os.walk(path):
        for filename in filenames:

            try:
                img = None
                existing_image = None
                existing_record = None
                dest_path = None
                paths = None


                input_file_path = os.path.join(root, filename)
                input_file, input_ext = os.path.splitext(filename)
                app.logger.debug("Scanning: %s" % input_file_path)
                if input_ext in [".jpg", ".JPG"]:
                    index_jpeg_file(input_file_path)

                #files with extentions other that jpg
                else:
                    #Don't care about these files
                    if not input_file in [".DS_Store"]:
                        other_file_handler(input_file_path, input_file, input_ext)
            except OSError as e:
                app.logger.error("The file %s is damaged. Error: %s" % (input_file_path, e))

            except Exception as e:
                app.logger.error("An error occured while indexing %s. Error: %s" % (input_file_path, e))





def index_jpeg_file(input_file_path):

    #split file path into path, filename and extension
    p, input_file = os.path.split(input_file_path)
    input_file, input_ext = os.path.splitext(input_file)

    #get basic file information and populate the image object
    img = image(input_file_path)
    img.index_helper = ImageHelper(input_file_path)
    img.db_image_hash = img.index_helper.get_image_hash()
    img.db_size = os.path.getsize(input_file_path)
    img.db_extension = input_ext.lower()

    #get EXIF data and populate image object with exif data
    img.exif = img.index_helper.get_exif_data()
    if not img.index_helper.add_exif_to_image(img):
        #I have no exif!!
        no_exif_file_handler(input_file_path)
        return

    #generate new filename from exif date
    img.db_filename = img.index_helper.get_filename_from_date(img.db_date_taken)

    #check if the image already exists - first check based on digital hash of image, then on same filename
    existing_record = locate_image("db_image_hash", img.db_image_hash)
    if not existing_record:
        existing_record = locate_image("db_filename", img.db_filename)

    #Image does not exist in db - create
    if not existing_record:
        new_image_file_handler(img, input_file_path)

    else:
        #Create image object from db record
        existing_image = image(existing_record)
        existing_image_file_handler(img,existing_image, input_file_path )

        app.logger.debug("image exists")

def new_image_file_handler(img, soruce_file):
     #set basic paths
    img.db_original_subpath = img.index_helper.get_path_from_date(IMAGE_STORE, img.db_date_taken)
    img.db_original_path = os.path.join(img.db_original_subpath, img.db_filename) + img.db_extension

    # check  that the image file does not exist
    if not os.path.exists(img.db_original_path):
        #move the image to the image store
        img.index_helper.ensure_dirs_exist(img.db_original_subpath)
        move(soruce_file, img.db_original_path)

        #generate thumbs and web images
        dest_path = img.db_original_subpath.replace(IMAGE_STORE, IMAGE_THUMBS)
        paths = img.index_helper.generate_files(dest_path, img.db_filename, img.db_extension)
        img.db_large_path, img.db_medium_path, img.db_thumb_path = paths

        #save image object to db
        save_image(img)
        app.logger.debug("New image was saved to DB and path: %s" % img.db_original_path)
    else:
        app.logger.error("Image was not found in DB but did exist in file system. Filename: %s" % img.db_original_path)


def existing_image_file_handler(img, existing_image, soruce_file):
        #Ensure that the file does not exist - find new file name if it does
        img.db_filename = img.db_filename + "_det"
        img.db_original_subpath = img.index_helper.get_path_from_date(IMAGE_DETENTION, img.db_date_taken)

        img.db_filename = get_valid_filename(img.db_original_subpath,img.db_filename, img.db_extension)
        img.db_original_path = os.path.join(img.db_original_subpath, img.db_filename) + img.db_extension

        #move the image to the image detention
        img.index_helper.ensure_dirs_exist(img.db_original_subpath)
        move(soruce_file, img.db_original_path)

        #generate thumbs and web images
        dest_path = img.db_original_subpath.replace(IMAGE_DETENTION, IMAGE_THUMBS)
        paths = img.index_helper.generate_files(dest_path, img.db_filename, img.db_extension)
        img.db_large_path, img.db_medium_path, img.db_thumb_path = paths

        #save image object to db
        if not existing_image.db_size == img.db_size:
            app.logger.debug("An image with this exact timestamp already exists in the system but "
                             "has a different file size. A duplicate has been added to %s" % img.db_original_path)
            img.add_link(existing_image.db_id, 2)
        else:
            app.logger.debug("An image which appears to be an exact copy already exists in the system. "
                 "A duplicate has been added to %s" % img.db_original_path)
            img.add_link(existing_image.db_id, 1)

        img.db_tags.append({"category": "Indexer", "value": "Double"})
        img.set_tags()
        save_image(img)

def no_exif_file_handler(filepath):
    app.logger.info("This image (%s) has no EXIF data and has been left in %s" % (filepath, IMAGE_WATCH_FOLDER))
    pass

def other_file_handler(source, filename, extension):
    no_image = ImageHelper()
    dest_path = os.path.join(OTHER_FILES, extension.lstrip("."))

    no_image.ensure_dirs_exist(dest_path)
    dest_path = os.path.join(dest_path, filename) + extension
    if not os.path.exists(dest_path):
        move(source, dest_path)

    app.logger.debug("Moved %s to %s" % (source, dest_path))


def get_valid_filename(path, filename, extention):
    i = 0
    while True:
        full_path = os.path.join(path, filename) + extention
        if os.path.isfile(full_path):
            filename = filename.rstrip("_" + str(i))
            i += 1
            filename = "{}_{}".format(filename, i)
        else:
            return filename

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
        index_watcher()

