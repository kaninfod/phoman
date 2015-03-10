import os, errno
from bson.objectid import ObjectId
from PIL import Image, ImageOps
from PIL import ExifTags
from PIL.ExifTags import TAGS, GPSTAGS
from app import *
from bson import json_util
import json
import datetime
from geopy.geocoders import Nominatim




class imagebase():
    db_filename = ""
    db_original_path = ""
    db_large_path = ""
    db_medium_path = ""
    db_thumb_path = ""
    db_size = ""
    db_make = ""
    db_model = ""
    db_ImageUniqueID = ""
    db_has_exif = ""
    db_id = ""
    db_date_taken = ""
    db_latitude = ""
    db_longitude = ""

    def __mongo_attributes__(self):

        return [i for i in dir(self)  if i.startswith('db_')]

    def __mongo_save__(self):
        imgobject = {}

        for field in self.__mongo_attributes__():
            imgobject[field] = getattr(self,field)
        im_id = imagesDB.update({"date_taken":self.db_date_taken}, {"$set":imgobject}, upsert=True)




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
            self._image_from_db(imageSource)



    def _image_from_file(self, file):

        try:
            self.exif = self._get_exif(file)

            if self.exif == None:
                self.db_has_exif = False
                self.db_date_taken = datetime.datetime(1972,6,24,0)
            else:
                if "DateTimeOriginal" in self.exif:
                    photoDate = str(self.exif["DateTimeOriginal"])
                elif "DateTime" in self.exif:
                    photoDate = str(self.exif["DateTime"])
                self.db_date_taken = datetime.datetime.strptime(photoDate, "%Y:%m:%d %H:%M:%S")


                if "Make" in self.exif:
                    self.db_make = self.exif["Make"]

                if "Model" in self.exif:
                    self.db_model = self.exif["Model"]

                if "ImageUniqueID" in self.exif:
                    self.db_ImageUniqueID = self.exif["ImageUniqueID"]

                self.db_latitude, self.db_longitude = get_lat_lon(self.exif)

                geolocator = Nominatim()
                location = geolocator.reverse("%s,%s2" % (self.db_latitude, self.db_longitude))
                print(location)

                self.db_has_exif = True

            self._generate_files(file)
        except Exception as e:
            print(e.args[0])

        self.__mongo_save__()



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
        im_id = imagesDB.update({"date_taken":self.db_date_taken}, {"$set":imgobject}, upsert=True)



    def _get_exif(self, file):

        """Returns a dictionary from the exif data of an PIL Image item. Also converts the GPS Tags"""
        exif_data = {}
        image=Image.open(file,'r')
        info = image._getexif()
        if info:
            for tag, value in info.items():
                decoded = TAGS.get(tag, tag)
                if decoded == "GPSInfo":
                    gps_data = {}
                    for gps_tag in value:
                        sub_decoded = GPSTAGS.get(gps_tag, gps_tag)
                        gps_data[sub_decoded] = value[gps_tag]

                    exif_data[decoded] = gps_data
                else:
                    exif_data[decoded] = value

        return exif_data


        # try:
        #     imgFile=Image.open(file,'r')
        #     exif = {
        #         ExifTags.TAGS[k]: v
        #         for k, v in imgFile._getexif().items()
        #         if k in ExifTags.TAGS
        #     }
        #
        #
        #     return exif
        #except Exception as e:
        #    return None

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


def get_exif_data(image):
    """Returns a dictionary from the exif data of an PIL Image item. Also converts the GPS Tags"""
    exif_data = {}
    info = image._getexif()
    if info:
        for tag, value in info.items():
            decoded = TAGS.get(tag, tag)
            if decoded == "GPSInfo":
                gps_data = {}
                for gps_tag in value:
                    sub_decoded = GPSTAGS.get(gps_tag, gps_tag)
                    gps_data[sub_decoded] = value[gps_tag]

                exif_data[decoded] = gps_data
            else:
                exif_data[decoded] = value

    return exif_data

def _convert_to_degress(value):
    """Helper function to convert the GPS coordinates stored in the EXIF to degress in float format"""
    deg_num, deg_denom = value[0]
    d = float(deg_num) / float(deg_denom)

    min_num, min_denom = value[1]
    m = float(min_num) / float(min_denom)

    sec_num, sec_denom = value[2]
    s = float(sec_num) / float(sec_denom)

    return d + (m / 60.0) + (s / 3600.0)

def get_lat_lon(exif_data):
    """Returns the latitude and longitude, if available, from the provided exif_data (obtained through get_exif_data above)"""
    lat = None
    lon = None

    if "GPSInfo" in exif_data:
        gps_info = exif_data["GPSInfo"]

        gps_latitude = gps_info.get("GPSLatitude")
        gps_latitude_ref = gps_info.get('GPSLatitudeRef')
        gps_longitude = gps_info.get('GPSLongitude')
        gps_longitude_ref = gps_info.get('GPSLongitudeRef')

        if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
            lat = _convert_to_degress(gps_latitude)
            if gps_latitude_ref != "N":
                lat *= -1

            lon = _convert_to_degress(gps_longitude)
            if gps_longitude_ref != "E":
                lon *= -1

    return lat, lon