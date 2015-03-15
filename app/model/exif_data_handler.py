__author__ = 'hingem'
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from PIL.ExifTags import TAGS, GPSTAGS

from app import *


def get_exif_data(image):
    """Returns a dictionary from the exif data of an PIL Image item. Also converts the GPS Tags"""

    info = image._getexif()
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
            if location:
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