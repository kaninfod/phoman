__author__ = 'hingem'
import hashlib
import os
from datetime import datetime

from PIL.ExifTags import TAGS, GPSTAGS
from PIL import Image, ImageOps

from phototank.app import *


class ImageHelper():
    image = None
    exif_data = None

    def __init__(self, filename=None):
        if filename:

            self.image = Image.open(filename, 'r')
            self.exif = self.get_exif_data()

    def get_exif_data(self):
        """Returns a dictionary from the exif data of an PIL Image item. Also converts the GPS Tags"""

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
            img.has_exif = True
            self._add_exif_data(img, "Make", "make")
            self._add_exif_data(img, "Model", "model")
            self._add_exif_data(img, "ImageUniqueID", "ImageUniqueID")
            self._add_exif_data(img, "ExifImageHeight", "original_height")
            self._add_exif_data(img, "ExifImageWidth", "original_width")
            self._add_exif_data(img, "Orientation", "orientation")
            self._add_exif_data(img, "Flash", "flash_fired")



            #img.location.latitude, img.location.longitude = self.get_lat_lon(img.exif)

            #if not img.location.latitude or not img.location.longitude:
            #    img.location.status = -2
            #else:
            #    img.location.status = 0

            exif_date_fields = ["DateTimeOriginal", "DateTime"]
            for date_field in exif_date_fields:
                if date_field in img.exif:
                    date_string = str(img.exif[date_field])
                    date_format = "%Y:%m:%d %H:%M:%S"
                    date = datetime.strptime(date_string, date_format)
                    setattr(img, "date_taken", date)
                    break
            return True
        else:
            img.has_exif = False
            return False

    def _add_exif_data(self, img, exif_field, mongo_field):

        if exif_field in img.exif:
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


    def generate_files(self, dest_path, filename, ext):
        src_path = os.path.join(dest_path, filename) + ext
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

    def _convert_to_degress(self, value):
        """Helper function to convert the GPS coordinates stored in the EXIF to degress in float format"""
        deg_num, deg_denom = value[0]
        d = float(deg_num) / float(deg_denom)

        min_num, min_denom = value[1]
        m = float(min_num) / float(min_denom)

        sec_num, sec_denom = value[2]
        s = float(sec_num) / float(sec_denom)

        return d + (m / 60.0) + (s / 3600.0)


    def get_lat_lon(self):
        """Returns the latitude and longitude, if available, from the provided exif_data (obtained through get_exif_data above)"""
        lat = None
        lon = None
        if not self.exif:
            return False, False
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





