__author__ = 'hingem'


from shutil import move
import argparse

from photo_tank.model.photo import Photo
from photo_tank.model.Image_helper import *
from photo_tank.app import app
import errno


def index_watcher():

    os.system("")
    path = app.config["IMAGE_WATCH_FOLDER"]

    app.logger.info("Indexing of %s initiated" % app.config["IMAGE_WATCH_FOLDER"])
    for root, dirnames, filenames in os.walk(path):
        for filename in filenames:

            try:

                # Set basic file data
                input_file_path = os.path.join(root, filename)
                input_file, input_ext = os.path.splitext(filename)
                app.logger.debug("Scanning: %s" % input_file_path)

                # Index JPEG files - Move other files to OTHER folder
                if input_ext in [".jpg", ".JPG"]:
                    index_jpeg_file(input_file_path)

                else:
                    # Don't care about these files
                    if not input_file in [".DS_Store"]:
                        other_file_handler(input_file_path, input_file, input_ext)

            except OSError as e:
                app.logger.error("The file %s is damaged. Error: %s" % (input_file_path, e))

            except Exception as e:
                app.logger.error("An error occured while indexing %s. Error: %s" % (input_file_path, e))

    app.logger.info("Indexing of %s ended" % app.config["IMAGE_WATCH_FOLDER"])

def index_jpeg_file(input_file_path):

    # split file path into path, filename and extension
    p, input_file = os.path.split(input_file_path)
    input_file, input_ext = os.path.splitext(input_file)

    # get basic file information and populate the image object
    img = Photo(input_file_path)
    img.index_helper = ImageHelper(input_file_path)
    img.image_hash = img.index_helper.get_image_hash()
    img.files.size = os.path.getsize(input_file_path)
    img.files.extension = input_ext.lower()

    #get EXIF data and populate image object with exif data
    img.exif = img.index_helper.get_exif_data()
    if not img.index_helper.add_exif_to_image(img):
        #I have no exif!!
        no_exif_file_handler(input_file_path)
        return 0

    #generate new filename from exif date
    img.files.filename = get_filename_from_date(img.date_taken)

    path = new_image_file_handler(img, input_file_path)
    return img

def new_image_file_handler(img, soruce_file):

    #check if the image already exists - first check based on digital hash of image, then on same filename
    existing_record = app.db.locate_image("image_hash", img.image_hash)
    if not existing_record:
            existing_record = app.db.locate_image("files.filename", img.files.filename)

    #save photo to get id. Upsert is false meaning that if similar record exists we till create duplicate
    app.db.save_photo(img, upsert=False)

    # set basic paths
    img.files.original_subpath = get_path_from_date(app.config["IMAGE_STORE"], img.date_taken)
    img.files.original_path = os.path.join(img.files.original_subpath, img.id) + img.files.extension

    # check  that the image file does not exist
    if not os.path.exists(img.files.original_path):
        # move the image to the image store
        ensure_dirs_exist(img.files.original_subpath)
        move(soruce_file, img.files.original_path)

        #generate thumbs and web images
        dest_path = img.files.original_subpath.replace(app.config["IMAGE_STORE"], app.config["IMAGE_THUMBS"])
        ensure_dirs_exist(dest_path)
        paths = img.index_helper.generate_files(dest_path, img.id, img.files.extension)
        img.files.large_path, img.files.medium_path, img.files.thumb_path = paths

        #Image does not exist in db - create
        if existing_record:
            app.logger.debug("image exists")
            #Create image object from db record
            existing_image = Photo(existing_record)
            img.tags.append({"category": "Indexer", "value": "Double"})
            existing_image.tags.append({"category": "Indexer", "value": "Double"})

            # save image object to db and create db link to sibling
            # links:
            #     1: images are digitally the same
            #     2: images has alike time stamps but size differs
            if not existing_image.files.size == img.files.size:
                app.logger.debug("An image with this exact timestamp already exists in the system but "
                                 "has a different file size. A duplicate has been added to %s" % img.files.original_path)
                img.add_link(existing_image.id, 2)
                existing_image.add_link(img.id, 2)

            else:
                app.logger.debug("An image which appears to be an exact copy already exists in the system. "
                                 "A duplicate has been added to %s" % img.files.original_path)
                img.add_link(existing_image.id, 1)
                existing_image.add_link(img.id, 1)

            #save any changes made to the existing photo
            app.db.save_photo(existing_image)

        #set tags and save photo
        img.set_tags()
        app.db.save_photo(img)
        app.logger.debug("New image was saved to DB and path: %s" % img.files.original_path)

    else:
        app.logger.error("Image was not found in DB but did exist in file system. Filename: %s" % img.files.original_path)


def no_exif_file_handler(filepath):
    app.logger.info("This image (%s) has no EXIF data and has been left in %s" % (filepath, app.config["IMAGE_WATCH_FOLDER"]))
    pass


def other_file_handler(source, filename, extension):

    dest_path = os.path.join(app.config["OTHER_FILES"], extension.lstrip("."))

    ensure_dirs_exist(dest_path)
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

def get_filename_from_date(date):
    _year = date.strftime("%Y")
    _month = date.strftime("%m")
    _day = date.strftime("%d")
    _hour = date.strftime("%H")
    _minute = date.strftime("%M")
    _second = date.strftime("%S")

    destination_file_name = "%s%s%s_%s%s%s" % (_year, _month, _day, _hour, _minute, _second)
    destination_file_name = destination_file_name.lower()
    return destination_file_name

def get_path_from_date(base_path, date):

    _year = date.strftime("%Y")
    _month = date.strftime("%m")
    _day = date.strftime("%d")

    path = os.path.join(base_path, _year, _month, _day)
    return path

def ensure_dirs_exist(dirname):
    """
    Ensure that a named directory exists; if it does not, attempt to create it.
    """
    try:
        os.makedirs(dirname)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

if __name__ == "__main__":

        index_watcher()

