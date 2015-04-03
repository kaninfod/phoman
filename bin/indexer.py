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
    path = app.config["IMAGE_WATCH_FOLDER"]
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
                if input_ext in [".jpg", ".JPG"]:
                    index_jpeg_file(input_file_path)

                #files with extentions other that jpg
                else:

                    if not input_file in [".DS_Store"]:

                        no_image = ImageHelper()
                        dest_path = os.path.join(app.config["OTHER_FILES"], input_ext.lstrip("."))

                        no_image.ensure_dirs_exist(dest_path)
                        dest_path = os.path.join(dest_path, input_file) + input_ext
                        if not os.path.exists(dest_path):
                            move(input_file_path, dest_path)

            except OSError as e:
                app.logger.debug("The file %s is damaged. Error: %s" % (input_file_path, e))

            except Exception as e:
                app.logger.debug("An error occured while indexing %s. Error: %s" % (input_file_path, e))





def index_jpeg_file(input_file_path):


    app.logger.debug("scanning: %s" % input_file_path)

    #split file path into path, filename and extension
    p, input_file = os.path.split(input_file_path)
    input_file, input_ext = os.path.splitext(input_file)

    #get basic file information and populate the image object
    img = image(input_file_path)
    img_helper = ImageHelper(input_file_path)
    img.db_image_hash = img_helper.get_image_hash()
    img.db_size = os.path.getsize(input_file_path)
    img.db_extension = input_ext.lower()

    #get EXIF data and populate image object with exif data
    img.exif = img_helper.get_exif_data()
    if not img.exif is None:
        img.db_has_exif = True
        img_helper.add_exif_data(img, "Make", "db_make")
        img_helper.add_exif_data(img, "Model", "db_model")
        img_helper.add_exif_data(img, "ImageUniqueID", "db_ImageUniqueID")
        img_helper.add_exif_data(img, "ExifImageHeight", "db_original_height")
        img_helper.add_exif_data(img, "ExifImageWidth", "db_original_width")
        img_helper.add_exif_data(img, "Orientation", "db_orientation")
        img_helper.add_exif_data(img, "Flash", "db_flash_fired")
        img.db_latitude, img.db_longitude = img_helper.get_lat_lon(img.exif)
        if not img_helper.add_exif_data(img, "DateTimeOriginal", "db_date_taken"):
            if not img_helper.add_exif_data(img, "DateTimeOriginal", "db_date_taken"):
                img.db_date_taken = datetime(1972, 6, 24, 0)
    else:
        #Incase file has no exif
        img.db_has_exif = False
        img.db_date_taken = datetime(1972, 6, 24, 0)

    #generate new filename from exif date
    img.db_filename = img_helper.get_filename_from_date(img.db_date_taken)

    #check if the image already exists - first check based on digital hash of image, then on same filename
    existing_record = locate_image("db_image_hash", img.db_image_hash)
    if not existing_record:
        existing_record = locate_image("db_filename", img.db_filename)

    #Image does not exist in db - create
    if not existing_record:

        #set basic paths
        img.db_original_subpath = img_helper.get_path_from_date(app.config["IMAGE_STORE"], img.db_date_taken)
        img.db_original_path = os.path.join(img.db_original_subpath, img.db_filename) + img.db_extension

        # check  that the image file does not exist
        if not os.path.exists(img.db_original_path):
            #move the image to the image store
            img_helper.ensure_dirs_exist(img.db_original_subpath)
            move(input_file_path, img.db_original_path)

            #generate thumbs and web images
            dest_path = img.db_original_subpath.replace(app.config["IMAGE_STORE"], app.config["IMAGE_THUMBS"])
            paths = img_helper.generate_files(dest_path, img.db_filename, img.db_extension)
            img.db_large_path, img.db_medium_path, img.db_thumb_path = paths

            #save image object to db
            save_image(img)
        else:
            print("Delete image from db and leave in watch folder for next run")
    else:
        #Create image object from db record
        existing_image = image(existing_record)

        #Ensure that the file does not exist - find new file name if it does
        img.db_filename = img.db_filename + "_det"
        img.db_original_subpath = img_helper.get_path_from_date(app.config["IMAGE_DETENTION"], img.db_date_taken)
        i = 0
        while True:
            img.db_original_path = os.path.join(img.db_original_subpath, img.db_filename) + img.db_extension
            if os.path.isfile(img.db_original_path):
                img.db_filename = img.db_filename.rstrip("_" + str(i))
                i += 1
                img.db_filename = "{}_{}".format(img.db_filename, i)
            else:
                break

        #move the image to the image detention
        img_helper.ensure_dirs_exist(img.db_original_subpath)
        move(input_file_path, img.db_original_path)

        #generate thumbs and web images
        dest_path = img.db_original_subpath.replace(app.config["IMAGE_DETENTION"], app.config["IMAGE_THUMBS"])
        paths = img_helper.generate_files(dest_path, img.db_filename, img.db_extension)
        img.db_large_path, img.db_medium_path, img.db_thumb_path = paths

        #save image object to db
        if not existing_image.db_size == img.db_size:
            img.add_link(existing_image.db_id, 2)
        else:
            img.add_link(existing_image.db_id, 1)

        img.db_tags.append({"category": "Indexer", "value": "Double"})
        img.set_tags()
        save_image(img)


        app.logger.debug("image exists")



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

