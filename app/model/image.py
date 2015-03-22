import os
import errno
import json
import datetime

from bson.objectid import ObjectId
from PIL import Image, ImageOps
from bson import json_util

from app import *
from app.model.exif_data_handler import get_exif_data, get_lat_lon, lookup_location


class ImageBase():
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
        imgobject = {}

        for field in self.__mongo_attributes__():
            if not field == "db_id":
                imgobject[field] = getattr(self, field)

        imagesDB.update({"date_taken": self.db_date_taken}, {"$set": imgobject}, upsert=True)
        self.db_id = str(imagesDB.find(imgobject)[0]["_id"])


    def __mongo_populate__(self, record):

        for field in record:
            if field == "_id":
                setattr(self, "db_id", str(record["_id"]))
            elif "db_" in field:
                setattr(self, field, record[field])


class ImageQuery(ImageBase):
    def __init__(self):
        self._query = {}
        self.date_taken_gte = ""
        self.date_taken_lt = ""

    def gt_date(self, date, date_field="date_taken"):
        if isinstance(date, datetime.date):
            date = self._date_to_datetime(date)

        if date_field in self._query:
            self._query[date_field].update({"$gte": date})
        else:
            self._query[date_field] = {"$gte": date}

        self.date_taken_gte = date

    def lt_date(self, date, date_field="date_taken"):
        if isinstance(date, datetime.date):
            date = self._date_to_datetime(date)

        if date_field in self._query:
            self._query[date_field].update({"$lt": date})
        else:
            self._query[date_field] = {"$lt": date}

        self.date_taken_lt = date

    def __setattr__(self, name, value):
        _blacklist = ["_query", "date_taken_lt", "date_taken_gte"]
        if not name in _blacklist and value != "":
            self._query[name] = value
        object.__setattr__(self, name, value)

    @staticmethod
    def _date_to_datetime(date):
        return datetime.datetime.combine(date, datetime.time.min)

    @property
    def query(self):
        if self._query:
            return json.dumps(self._query, default=json_util.default)
        else:
            return None

    @query.setter
    def query(self, value):
        self._query = json.loads(value, object_hook=json_util.object_hook)


    def serialize(self):
        t = self.__dict__.copy()
        t.pop("_query")
        t.update({"query": self.query})

        return t
        # return json.dumps(self.__dict__, default=json_util.default)


def generate_thumb(image, path, size):
    if not os.path.isfile(path):
        thumb = ImageOps.fit(image, size, Image.ANTIALIAS)
        thumb.save(path, "JPEG")


class image(ImageBase):
    THUMB_SIZE = (256, 256)
    MEDIUM_SIZE = (600, 800)
    LARGE_SIZE = (1024, 1200)


    def __init__(self, image_source=None, image_id=None, update_location=False):
        self.db_tags = []

        if image_id:
            image_source = imagesDB.find_one({'_id': ObjectId(image_id)})

        if isinstance(image_source, str):
            self._image_from_file(image_source)
        else:
            self.__mongo_populate__(image_source)
            if update_location:
                lookup_location(self)


    def _image_from_file(self, file):

        image = Image.open(file, 'r')
        self.exif = get_exif_data(image)

        if self.exif is None:
            self.db_has_exif = False
            self.db_date_taken = datetime.datetime(1972, 6, 24, 0)
        else:

            if "ImageUniqueID" in self.exif:
                db_entry = imagesDB.find_one({'db_ImageUniqueID': self.exif['ImageUniqueID']})
                if db_entry:
                    self.db_country = db_entry["db_country"]
                    self.db_state = db_entry["db_state"]
                    self.db_road = db_entry["db_road"]
                    self.db_address = db_entry["db_address"]
                    self.db_location = db_entry["db_location"]

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

    def add_location_data(self):


        if not self.db_location and self.db_latitude and self.db_longitude:
            print(self.db_location)
            point = "%s,%s" % (self.db_latitude, self.db_longitude)
            location = lookup_location(point)

            if location:
                if "error" in location.raw:
                    print(location.raw["error"])
                elif "address" in location.raw:
                    if "country" in location.raw["address"]:
                        self.db_country = location.raw["address"]['country']
                    if "state" in location.raw["address"]:
                        self.db_state = location.raw["address"]['state']
                    if "road" in location.raw["address"]:
                        self.db_road = location.raw["address"]['road']

                    self.db_address = location.raw['display_name']

                    self.db_location = True
                else:
                    print()
            else:
                self.db_location = False
        else:
            print(self.db_location)

    def set_tags(self):

        self.db_tags = []
        self.db_tags.append(self.db_date_taken.strftime("%B"))
        self.db_tags.append(self.db_date_taken.strftime("%Y"))
        self.db_tags.append(self.db_date_taken.strftime("%A"))
        self.db_tags.append("Week " + self.db_date_taken.strftime("%U"))

        self.db_tags.append(self.db_model)
        self.db_tags.append(self.db_make)

        if self.db_country:
            self.db_tags.append(self.db_country)

        if self.db_state:
            self.db_tags.append(self.db_state)

        if not self.db_location:
            self.db_tags.append("No Location")

        if self.db_has_exif:
            self.db_tags.append("No EXIF")

        if 5 <= self.db_date_taken.hour < 12:
            self.db_tags.append("Morning")
        if 12 <= self.db_date_taken.hour < 17:
            self.db_tags.append("Afternoon")
        if 17 <= self.db_date_taken.hour < 23:
            self.db_tags.append("Evening")
        if 23 <= self.db_date_taken.hour < 5:
            self.db_tags.append("Night")

        if self.db_size <= 1024000:
            self.db_tags.append("Small file")
        if 1024000 < self.db_size < 3600000:
            self.db_tags.append("Medium file")
        if self.db_size >= 3600000:
            self.db_tags.append("Large file")


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

        im = Image.open(self.db_original_path)
        self.generate_image(im, self.db_medium_path, self.MEDIUM_SIZE)
        generate_thumb(im, self.db_thumb_path, self.THUMB_SIZE)

    def generate_image(self, image, path, size):

        if not os.path.isfile(self.db_medium_path):
            image.thumbnail(size, Image.ANTIALIAS)
            image.save(path, "JPEG")


    def _ensure_dir(self, dirname):
        """
        Ensure that a named directory exists; if it does not, attempt to create it.
        """
        try:
            os.makedirs(dirname)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise


