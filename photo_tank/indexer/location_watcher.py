__author__ = 'hingem'

from photo_tank.model.photo import Photo
from photo_tank.app import app
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut


def lookup_location(image, location):
    # Image location statuses:
    #   -2 : no gps data available
    #   -1 : gps data available but lookup unsuccessful
    #   0  : gps data available but no lookup attempted
    #   1  : gps data available and lookup successful


    # app.logger.name = "lookup location"
    if not location.status == -2:

        geolocator = Nominatim(timeout=4)

        point = "%s,%s" % (location.latitude, location.longitude)
        app.logger.debug("Looking up %s" % image.id)
        loc = None
        try:
            loc = geolocator.reverse(point)
        except GeocoderTimedOut as e:
            app.logger.warning(e)
            location.status = -1
            return -1
        except Exception as e:
            app.logger.warning(e)
            location.status = -1
            return -1
        else:
            if "error" in loc.raw:
                app.logger.warning(location.raw["error"])
                location.status = -1
                return -1
            elif "address" in loc.raw:
                if "country" in loc.raw["address"]:
                    location.country = loc.raw["address"]['country']
                    app.logger.debug("success getting country")

                if "state" in loc.raw["address"]:
                    location.state = loc.raw["address"]['state']
                    app.logger.debug("success getting state")

                if "city" in loc.raw["address"]:
                    location.city = loc.raw["address"]['city']
                    app.logger.debug("success getting city")

                if "suburb" in loc.raw["address"]:
                    location.suburb = loc.raw["address"]['suburb']
                    app.logger.debug("success getting suburb")

                if "postcode" in loc.raw["address"]:
                    location.postcode = loc.raw["address"]['postcode']
                    app.logger.debug("success getting postcode")

                if "road" in loc.raw["address"]:
                    location.road = loc.raw["address"]['road']
                    app.logger.debug("success getting road")

                location.address = loc.raw['display_name']


                app.logger.info("success getting one or more location entities")
                location.status = 1
                return 1
            else:
                app.logger.info("no location returned")
                location.status = -1
                return -1

    else:
        app.logger.debug("No coordinates, id: %s" % image.id)


def location_watcher():
    images = app.db.get_photos({'location.status':0})

    for img in images:
        photo = Photo(img)
        #ih = ImageHelper(photo.files.original_path)
        lookup_location(photo,photo.location)
        app.db.save_photo(photo)

if __name__ == "__main__":
    location_watcher()