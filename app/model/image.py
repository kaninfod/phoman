import os, errno
from bson.objectid import ObjectId
from PIL import Image, ImageOps

from app import *
from bson import json_util
import json
import datetime
from geopy.geocoders import Nominatim
from app.model.exif_data_handler import get_exif_data, get_lat_lon



class imagebase():
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



    def __mongo_attributes__(self):

        return [i for i in dir(self)  if i.startswith('db_')]

    def __mongo_save__(self):
        imgobject = {}

        for field in self.__mongo_attributes__():
            if not field == "db_id":
                imgobject[field] = getattr(self,field)
        im_id = imagesDB.update({"date_taken":self.db_date_taken}, {"$set":imgobject}, upsert=True)

    def __mongo_populate__(self, record):
        blacklist = [ "exif"]
        for field in self.__mongo_attributes__():
            if field == "db_id":
                setattr(self,"db_id",str(record["_id"]))
            else:
                setattr(self,field,record[field])


class image_query(imagebase):

    def __init__(self):
        self._query = {}
        self.date_taken_gte = ""
        self.date_taken_lt = ""

    def gt_date(self, date, date_field="date_taken"):
        if isinstance(date, datetime.date):
            date = self._date_to_datetime(date)

        if date_field in self._query:
            self._query[date_field].update({"$gte":date})
        else:
            self._query[date_field] = {"$gte":date}

        self.date_taken_gte = date

    def lt_date(self, date, date_field="date_taken"):
        if isinstance(date, datetime.date):
            date = self._date_to_datetime(date)

        if date_field in self._query:
            self._query[date_field].update({"$lt":date})
        else:
            self._query[date_field] = {"$lt":date}

        self.date_taken_lt = date

    def __setattr__(self, name, value):
        _blacklist = ["_query", "date_taken_lt", "date_taken_gte"]
        if not name in _blacklist and value != "":
            self._query[name] = value
        object.__setattr__(self, name, value)

    def _date_to_datetime(self, date):
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
        t.update( {"query":self.query} )

        return t
        #return json.dumps(self.__dict__, default=json_util.default)


class image(imagebase):
    THUMB_SIZE = (256,256)
    MEDIUM_SIZE = (600,800)
    LARGE_SIZE = (1024,1200)

    def __init__(self, imageSource=None, id=None):
        if id:
            imageSource = imagesDB.find_one({'_id':ObjectId(id)})

        if isinstance(imageSource, str):
            self._image_from_file(imageSource)
        else:
            self.__mongo_populate__(imageSource)



    def _image_from_file(self, file):


        image=Image.open(file,'r')
        self.exif = get_exif_data(image)

        if self.exif == None:
            self.db_has_exif = False
            self.db_date_taken = datetime.datetime(1972,6,24,0)
        else:


            if not self.add_exif_data("DateTimeOriginal", "db_date_taken"):
                if not self.add_exif_data("DateTimeOriginal", "db_date_taken"):
                    self.db_date_taken = datetime.datetime(1972,6,24,0)

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
        self.__mongo_save__()

            #geolocator = Nominatim()
            #location = geolocator.reverse("%s,%s2" % (self.db_latitude, self.db_longitude))
            #print(location)

    def add_exif_data(self, exif_field, mongo_field):
        date_fields = ["DateTimeOriginal", "DateTime"]

        if exif_field in self.exif:
            if exif_field in date_fields:
                date_string = str(self.exif[exif_field])
                date_format = "%Y:%m:%d %H:%M:%S"
                date = datetime.datetime.strptime(date_string, date_format)
                setattr(self,mongo_field,date)
            else:
                setattr(self,mongo_field,self.exif[exif_field])
            return 1

    def __str__(self):
        return self.path

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
        self.generate_thumb(im, self.db_thumb_path,self.THUMB_SIZE)

    def generate_image(self, image, path, size):

        if not os.path.isfile(self.db_medium_path):
            image.thumbnail(size, Image.ANTIALIAS)
            image.save(path, "JPEG")


    def generate_thumb(self, image, path, size):

        if not os.path.isfile(path):
            thumb = ImageOps.fit(image, size, Image.ANTIALIAS)
            thumb.save(path, "JPEG")

    def _ensure_dir(self,dirname):
        """
        Ensure that a named directory exists; if it does not, attempt to create it.
        """
        try:
            os.makedirs(dirname)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise


