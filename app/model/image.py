import os
import errno

import datetime


from PIL import Image, ImageOps
from app import *
from app.model.exif_data_handler import get_exif_data, get_lat_lon, lookup_location
from app.model.mongo_db import get_image, save_image, locate_image


class image():
    db_filename = None
    db_original_path = None
    db_large_path = None
    db_medium_path = None
    db_thumb_path = None
    db_size = None
    db_make = None
    db_model = None
    db_ImageUniqueID = None
    db_has_exif = None
    db_id = None
    db_date_taken = None
    db_latitude = None
    db_longitude = None
    db_original_height = None
    db_original_width = None
    db_orientation = None
    db_flash_fired = None
    db_tags = []
    db_location = False
    db_country = None
    db_state = None
    db_address = None
    db_road = None


    def __mongo_attributes__(self):

        return [i for i in dir(self) if i.startswith('db_')]

    def __mongo_save__(self):
        save_image(self)



    def __mongo_populate__(self, record):

        for field in record:
            if field == "_id":
                setattr(self, "db_id", str(record["_id"]))
            elif "db_" in field:
                setattr(self, field, record[field])



    def __init__(self, image_source=None, image_id=None, update_location=False):
        self.db_tags = []

        if image_id:
            self.__mongo_populate__(get_image(image_id))

        else:
            if isinstance(image_source, str):
                self._image_from_file(image_source)
                print()
            elif isinstance(image_source, dict):
                self.__mongo_populate__(image_source)
                if update_location:
                    lookup_location(self)


    def _image_from_file(self, file):
        try:
            image = Image.open(file, 'r')
            self.exif = get_exif_data(image)

            if self.exif is None:
                self.db_has_exif = False
                self.db_date_taken = datetime.datetime(1972, 6, 24, 0)
            else:

                if "ImageUniqueID" in self.exif:
                    record = locate_image("db_ImageUniqueID", self.db_ImageUniqueID)
                    if record:
                        self.db_country = record["db_country"]
                        self.db_state = record["db_state"]
                        self.db_road = record["db_road"]
                        self.db_address = record["db_address"]
                        self.db_location = record["db_location"]

                if not self.add_exif_data("DateTimeOriginal", "db_date_taken"):
                    if not self.add_exif_data("DateTimeOriginal", "db_date_taken"):
                        self.db_date_taken = datetime.datetime(1972, 6, 24, 0)

                self.db_has_exif = True
                self.add_exif_data("Make", "db_make")
                self.add_exif_data("Model", "db_model")
                self.add_exif_data("ImageUniqueID", "db_ImageUniqueID")
                self.add_exif_data("ExifImageHeight", "db_original_height")
                self.add_exif_data("ExifImageWidth", "db_original_width")
                self.add_exif_data("Orientation", "db_orientation")
                self.add_exif_data("Flash", "db_flash_fired")
                self.db_latitude, self.db_longitude = get_lat_lon(self.exif)


            self._generate_files(file)
            self.set_tags()
            self.__mongo_save__()
        except OSError as e:
            app.logger.debug("The file %s is damaged. Error: %s" % (file, e))

        except Exception as e:
            app.logger.debug("An error occured while indexing %s. Error: %s" % (file, e))

    def set_tags(self):

        self.db_tags = []



        #time tags
        category = "Time"
        self.db_tags.append({"category": category, "value": self.db_date_taken.strftime("%B")})
        self.db_tags.append({"category": category, "value":  self.db_date_taken.strftime("%Y")})
        self.db_tags.append({"category": category, "value":  self.db_date_taken.strftime("%A")})
        self.db_tags.append({"category": category, "value":  "Week " + self.db_date_taken.strftime("%U")})

        if 5 <= self.db_date_taken.hour < 12:
            self.db_tags.append({"category": category, "value": "Morning"})
        if 12 <= self.db_date_taken.hour < 17:
            self.db_tags.append({"category": category, "value": "Afternoon"})
        if 17 <= self.db_date_taken.hour < 23:
            self.db_tags.append({"category": category, "value":  "Evening"})
        if 23 <= self.db_date_taken.hour < 5:
            self.db_tags.append({"category": category, "value":  "Night"})

        category = "Camera"
        self.db_tags.append({"category": category, "value":  self.db_model})
        self.db_tags.append({"category": category, "value":  self.db_make})


        category = "File"
        if not self.db_has_exif:
            self.db_tags.append({"category": category, "value":  "No EXIF"})

        if self.db_size <= 1024000:
            self.db_tags.append({"category": category, "value":  "Small file"})
        if 1024000 < self.db_size < 3600000:
            self.db_tags.append({"category": category, "value":  "Medium file"})
        if self.db_size >= 3600000:
            self.db_tags.append({"category": category, "value":  "Large file"})


        category = "Location"
        if self.db_country:
            self.db_tags.append({"category": category, "value":  self.db_country})

        if self.db_state:
            self.db_tags.append({"category": category, "value":  self.db_state})

        if not self.db_location:
            self.db_tags.append({"category": category, "value":  "No Location"})


    def add_exif_data(self, exif_field, mongo_field):
        date_fields = ["DateTimeOriginal", "DateTime"]

        if exif_field in self.exif:
            if exif_field in date_fields:
                date_string = str(self.exif[exif_field])
                date_format = "%Y:%m:%d %H:%M:%S"
                date = datetime.datetime.strptime(date_string, date_format)
                setattr(self, mongo_field, date)

            else:
                setattr(self, mongo_field, self.exif[exif_field])

            return 1

    def __str__(self):
        return self.db_original_path

    def _generate_files(self, file):
        self.db_original_path = file
        self.db_filename = os.path.split(file)[1]
        _webimages_path = app.config["IMAGE_THUMBS"] + \
                          self.db_original_path.replace(app.config["IMAGE_STORE"], "").replace(self.db_filename, "")
        self._ensure_dir(_webimages_path)
        fn, ext = os.path.splitext(self.db_filename)
        self.db_thumb_path = "%s%s_tm%s" % (_webimages_path, fn, ext)
        self.db_medium_path = "%s%s_md%s" % (_webimages_path, fn, ext)
        self.db_large_path = "%s%s_lg%s" % (_webimages_path, fn, ext)
        self._generate_webimages()
        self.db_size = os.path.getsize(file)

    def _generate_webimages(self):
        thumb_size = app.config["IMAGE_THUMB"]
        medium_size = app.config["IMAGE_MEDIUM"]
        large_size = app.config["IMAGE_LARGE"]

        im = Image.open(self.db_original_path)
        self.generate_image(im, self.db_medium_path, medium_size)
        self.generate_thumb(im, self.db_thumb_path, thumb_size)

    def generate_image(self, image, path, size):

        if not os.path.isfile(self.db_medium_path):
            image.thumbnail(size, Image.ANTIALIAS)
            image.save(path, "JPEG")

    def generate_thumb(self, image, path, size):
        if not os.path.isfile(path):
            thumb = ImageOps.fit(image, size, Image.ANTIALIAS)
            thumb.save(path, "JPEG")


    def _ensure_dir(self, dirname):
        """
        Ensure that a named directory exists; if it does not, attempt to create it.
        """
        try:
            os.makedirs(dirname)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise


