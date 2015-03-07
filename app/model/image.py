import os, errno
from bson.objectid import ObjectId
from datetime import datetime
from PIL import Image, ImageOps
from PIL import ExifTags
from app import *
from bson import json_util
import json
import datetime


class imagebase():

    def __init__(self):
        self.filename = ""
        self.original_path = ""
        self.large_path = ""
        self.medium_path = ""
        self.thumb_path = ""
        self.size = ""

        self.make = ""
        self.model = ""
        self.ImageUniqueID = ""

        self.has_exif = ""

        self.id = ""

        self.date_taken = ""

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
    def __init__(self, imageSource=None, id=None):


        if id:
            imageSource = imagesDB.find_one({'_id':ObjectId(id)})


        if isinstance(imageSource, str):
            self._image_from_file(imageSource)
        else:
            self._image_from_db(imageSource)


    def _generate_files(self, file):
        self.original_path = file
        self.filename = os.path.split(file)[1]
        _webimages_path = app.config["IMAGE_THUMBS"] + \
                          self.original_path.replace(app.config["IMAGE_STORE"], "").replace(self.filename, "")
        self._ensure_dir(_webimages_path)
        fn, ext = os.path.splitext(self.filename)
        self.thumb_path = "%s%s_tm%s" % (_webimages_path, fn, ext)
        self.medium_path = "%s%s_md%s" % (_webimages_path, fn, ext)
        self.large_path = "%s%s_lg%s" % (_webimages_path, fn, ext)
        self._generate_webimages()
        self.size = os.path.getsize(file)

    def _image_from_file(self, file):

        try:
            self.exif = self._get_exif(file)

            if self.exif == None:
                self.hasEXIF = False
            else:
                if "DateTimeOriginal" in self.exif:
                    photoDate = str(self.exif["DateTimeOriginal"])
                elif "DateTime" in self.exif:
                    photoDate = str(self.exif["DateTime"])
                self.date_taken = datetime.strptime(photoDate, "%Y:%m:%d %H:%M:%S")

                if "Make" in self.exif:
                    self.make = self.exif["Make"]

                if "Model" in self.exif:
                    self.model = self.exif["Model"]

                if "ImageUniqueID" in self.exif:
                    self.ImageUniqueID = self.exif["ImageUniqueID"]

                self.has_exif = True

                self._generate_files(file)
        except Exception as e:
            print(e.args[0])

        self._save()

    def _ensure_dir(self,dirname):
        """
        Ensure that a named directory exists; if it does not, attempt to create it.
        """
        try:
            os.makedirs(dirname)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

    def _image_from_db(self, record):
        blacklist = [ "exif"]
        for field in record:
            if not field in blacklist:
                if field == "_id":
                    setattr(self,"id",str(record[field]))
                else:
                    setattr(self,field,record[field])

    def _save(self):
        imgobject = {}
        blacklist = ["id", "exif"]
        for field in self.__dict__:
            if not field in blacklist:
                imgobject[field] = getattr(self,field)
        im_id = imagesDB.update({"date_taken":self.date_taken}, {"$set":imgobject}, upsert=True)



    def _get_exif(self, file):

        try:
            imgFile=Image.open(file,'r')
            exif = {
                ExifTags.TAGS[k]: v
                for k, v in imgFile._getexif().items()
                if k in ExifTags.TAGS
            }
            return exif
        except Exception as e:
            return None

    def __str__(self):
        return self.path

    def _generate_webimages(self):

        im = Image.open(self.original_path)

        size = 800, 640

        if not os.path.isfile(self.medium_path):

            im.thumbnail(size, Image.ANTIALIAS)
            im._save(self.medium_path, "JPEG")

        size = (256, 256)

        if not os.path.isfile(self.thumb_path):

            thumb = ImageOps.fit(im, size, Image.ANTIALIAS)
            thumb._save(self.thumb_path, "JPEG")
