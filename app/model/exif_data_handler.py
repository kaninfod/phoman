__author__ = 'hingem'
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from PIL.ExifTags import TAGS, GPSTAGS
import hashlib
from PIL import Image, ImageOps
import os
from datetime import datetime
import errno
from app import *

class ImageHelper():
    image = None
    exif_data = None

    def __init__(self, filename=None):
        if filename:
            self.image = Image.open(filename, 'r')
            self.exif = self.get_exif_data()

    def get_exif_data(self):
        """Returns a dictionary from the exif data of an PIL Image item. Also converts the GPS Tags"""

        #image = Image.open(file, 'r')
        info = self.image._getexif()
        if info is None:
            return None
        exif_data = {}
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

    def add_exif_to_image(self, img):
        if not self.exif is None:
            self.db_has_exif = True
            self._add_exif_data(img, "Make", "db_make")
            self._add_exif_data(img, "Model", "db_model")
            self._add_exif_data(img, "ImageUniqueID", "db_ImageUniqueID")
            self._add_exif_data(img, "ExifImageHeight", "db_original_height")
            self._add_exif_data(img, "ExifImageWidth", "db_original_width")
            self._add_exif_data(img, "Orientation", "db_orientation")
            self._add_exif_data(img, "Flash", "db_flash_fired")
            img.db_latitude, img.db_longitude = self.get_lat_lon(img.exif)
            if not self._add_exif_data(img, "DateTimeOriginal", "db_date_taken"):
                if not self._add_exif_data(img, "DateTime", "db_date_taken"):
                    img.db_date_taken = datetime(1972, 6, 24, 0)

            return True
        else:
            img.db_has_exif = False
            return False

    def _add_exif_data(self, img, exif_field, mongo_field):
        date_fields = ["DateTimeOriginal", "DateTime"]

        if exif_field in img.exif:
            if exif_field in date_fields:
                date_string = str(img.exif[exif_field])
                date_format = "%Y:%m:%d %H:%M:%S"
                date = datetime.strptime(date_string, date_format)
                setattr(img, mongo_field, date)

            else:
                setattr(img, mongo_field, img.exif[exif_field])

            return 1

    def get_image_hash(self):
        try:

            m = hashlib.md5()
            da = self.image.tostring()
            m.update(da)
            return m.hexdigest()

        except Exception as e:
            print(e)

    def get_filename_from_date(self, date):
        _year = date.strftime("%Y")
        _month = date.strftime("%m")
        _day = date.strftime("%d")
        _hour = date.strftime("%H")
        _minute = date.strftime("%M")
        _second = date.strftime("%S")

        destination_file_name = "%s%s%s_%s%s%s" % (_year, _month, _day, _hour, _minute, _second)
        destination_file_name = destination_file_name.lower()
        return destination_file_name

    def get_path_from_date(self, base_path, date):

        _year = date.strftime("%Y")
        _month = date.strftime("%m")
        _day = date.strftime("%d")

        path = os.path.join(base_path, _year, _month, _day)
        return path

    def generate_files(self, dest_path, filename, ext):
        src_path = os.path.join(dest_path, filename) + ext

        #dest_path = dest_path.replace(app.config["IMAGE_STORE"], app.config["IMAGE_THUMBS"])
        self.ensure_dirs_exist(dest_path)
        paths = []


        full_path = os.path.join(dest_path, "%s%s" % (filename, "_lg")) + ext
        self._generate_image(full_path, app.config["IMAGE_LARGE"])
        paths.append(full_path)


        full_path = os.path.join(dest_path, "%s%s" % (filename, "_md")) + ext
        self._generate_image(full_path, app.config["IMAGE_MEDIUM"])
        paths.append(full_path)


        full_path = os.path.join(dest_path, "%s%s" % (filename, "_tm")) + ext
        self._generate_thumb(full_path, app.config["IMAGE_THUMB"])
        paths.append(full_path)

        return paths

    def _generate_image(self, dest_path, size):
        if not os.path.isfile(dest_path):
            self.image.thumbnail(size, Image.ANTIALIAS)
            self.image.save(dest_path, "JPEG")

    def _generate_thumb(self, dest_path, size):
        if not os.path.isfile(dest_path):
            thumb = ImageOps.fit(self.image, size, Image.ANTIALIAS)
            thumb.save(dest_path, "JPEG")


    def ensure_dirs_exist(self, dirname):
        """
        Ensure that a named directory exists; if it does not, attempt to create it.
        """
        try:
            os.makedirs(dirname)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise


    def _convert_to_degress(self, value):
        """Helper function to convert the GPS coordinates stored in the EXIF to degress in float format"""
        deg_num, deg_denom = value[0]
        d = float(deg_num) / float(deg_denom)

        min_num, min_denom = value[1]
        m = float(min_num) / float(min_denom)

        sec_num, sec_denom = value[2]
        s = float(sec_num) / float(sec_denom)

        return d + (m / 60.0) + (s / 3600.0)


    def get_lat_lon(self, exif_data):
        """Returns the latitude and longitude, if available, from the provided exif_data (obtained through get_exif_data above)"""
        lat = None
        lon = None

        if "GPSInfo" in self.exif:
            gps_info = self.exif["GPSInfo"]

            gps_latitude = gps_info.get("GPSLatitude")
            gps_latitude_ref = gps_info.get('GPSLatitudeRef')
            gps_longitude = gps_info.get('GPSLongitude')
            gps_longitude_ref = gps_info.get('GPSLongitudeRef')

            if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
                lat = self._convert_to_degress(gps_latitude)
                if gps_latitude_ref != "N":
                    lat *= -1

                lon = self._convert_to_degress(gps_longitude)
                if gps_longitude_ref != "E":
                    lon *= -1

        return lat, lon


    def lookup_location(image):
        # app.logger.name = "lookup location"
        if not image.db_location and image.db_latitude and image.db_longitude:

            #geolocator = GoogleV3("AIzaSyCGSMJfmJI91d8S6q-LK-rSXO-HpJdZjQQ")
            geolocator = Nominatim(timeout=4)

            point = "%s,%s" % (image.db_latitude, image.db_longitude)
            app.logger.debug("Looking up %s" % image.db_id)
            try:
                location = geolocator.reverse(point)
            except GeocoderTimedOut as e:
                app.logger.warning(e)
            except Exception as e:
                app.logger.warning(e)
            else:
                if image.db_longitude and image.db_latitude:
                    if "error" in location.raw:
                        app.logger.warning(location.raw["error"])
                    elif "address" in location.raw:
                        if "country" in location.raw["address"]:
                            image.db_country = location.raw["address"]['country']
                            app.logger.debug("success getting country")
                        if "state" in location.raw["address"]:
                            image.db_state = location.raw["address"]['state']
                            app.logger.debug("success getting state")
                        if "road" in location.raw["address"]:
                            image.db_road = location.raw["address"]['road']
                            app.logger.debug("success getting road")

                        image.db_address = location.raw['display_name']

                        image.db_location = True
                        app.logger.info("success getting one or more location entities")
                    else:
                        app.logger.info("no location returned")
                else:
                    image.db_location = False
        else:
            app.logger.debug("No coordinates or image already located, id: %s" % image.db_id)


