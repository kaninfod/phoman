from peewee import *
from phototank.app import db
from geopy.distance import great_circle
from datetime import datetime
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import math


class Location(db.Model):
    status = IntegerField(null=True)
    latitude = FloatField(null=True)
    longitude = FloatField(null=True)
    location = TextField(null=True)
    country = TextField(null=True)
    state = TextField(null=True)
    address = TextField(null=True)
    road = TextField(null=True)
    city = TextField(null=True)
    suburb = TextField(null=True)
    postcode = TextField(null=True)

    def lookup_location(self):
        # Image location statuses:
        #   -2 : no gps data available
        #   -1 : gps data available but lookup unsuccessful
        #   0  : gps data available but no lookup attempted
        #   1  : gps data available and lookup successful


        # app.logger.name = "lookup location"
        if not self.status == -2:

            geolocator = Nominatim(timeout=4)

            point = "%s,%s" % (self.latitude, self.longitude)
            #app.logger.debug("Looking up %s" % self.id)
            loc = None
            try:
                loc = geolocator.reverse(point)
            except GeocoderTimedOut as e:
                #app.logger.warning(e)
                self.status = -1
                self.save()
                return -1
            except Exception as e:
                #app.logger.warning(e)
                self.status = -1
                self.save()
                return -1
            else:
                if "error" in loc.raw:
                    #app.logger.warning(loc.raw["error"])
                    self.status = -1
                    self.save()
                    return -1
                elif "address" in loc.raw:
                    if "country" in loc.raw["address"]:
                        self.country = loc.raw["address"]['country']
                        #app.logger.debug("success getting country")

                    if "state" in loc.raw["address"]:
                        self.state = loc.raw["address"]['state']
                        #app.logger.debug("success getting state")

                    if "city" in loc.raw["address"]:
                        self.city = loc.raw["address"]['city']
                        #app.logger.debug("success getting city")

                    if "suburb" in loc.raw["address"]:
                        self.suburb = loc.raw["address"]['suburb']
                        #app.logger.debug("success getting suburb")

                    if "postcode" in loc.raw["address"]:
                        self.postcode = loc.raw["address"]['postcode']
                        #app.logger.debug("success getting postcode")

                    if "road" in loc.raw["address"]:
                        self.road = loc.raw["address"]['road']
                        #app.logger.debug("success getting road")

                    self.address = loc.raw['display_name']


                    #app.logger.info("success getting one or more location entities")
                    self.status = 1
                    self.save()
                    return 1
                else:
                    #app.logger.info("no location returned")
                    self.status = -1
                    self.save()
                    return -1

        else:
            pass
            #app.logger.debug("No coordinates, id: %s" % self.id)


    def getpoint(self, lat, lon):
        min_dist_between_locations = 50
        offset_lat = 0.00005
        offset_lon = 0.000066

        close_to_locations = self.select() \
            .where( ( (Location.latitude.between(lat-offset_lat, lat+offset_lat)) | \
                      (Location.longitude.between(lon-offset_lon, lon+offset_lon))) )

        if not close_to_locations.count() == 0:
            dist_to_closest_location = min_dist_between_locations
            loc = self
            for location in close_to_locations:
                location1 = (lat,lon)
                location2 = (location.latitude, location.longitude)
                dist = great_circle(location1,location2)

                if dist.m < dist_to_closest_location:
                    loc = location
                    dist_to_closest_location = dist.m


            if dist_to_closest_location <= min_dist_between_locations:
                return loc.id

            else:
                return False


        else:
            self.latitude = lat
            self.longitude = lon
            self.save()
            self.lookup_location()

            return self.id





class Keyword(db.Model):
    value = TextField(null=True)
    category = TextField(null=True)
    subcategory = TextField(null=True)
    sortorder = IntegerField(null=True)
    count = IntegerField(null=True)

    def json(self, query=""):
        kw = self.select().group_by(Keyword.category, Keyword.sortorder, Keyword.subcategory, Keyword.value).where(Keyword.value.contains(query))
        js = []
        for k in kw:
            js.append({'category':k.category, 'subcategory':k.subcategory, 'value':k.value, 'id':str(k.id)})
            #js.append(k.value)
        #js = {"results":js}
        return js

    def keyword_tree(self):
        kw = self.select().group_by(Keyword.category, Keyword.sortorder, Keyword.subcategory, Keyword.value)
        kwd = {}
        cats = {}


        for w in kw:
            if not w.category in cats:
                cats.update({w.category:{w.subcategory:{w.value:w}}})
            elif not w.subcategory in cats[w.category]:
                cats[w.category].update({w.subcategory:{w.value:w}})
            elif not w.value in cats[w.category][w.subcategory]:
                cats[w.category][w.subcategory].update({w.value:w})

        for category, categories in cats.items():
            for subcategory, subcategories in categories.items():
                for value, details in subcategories.items():
                    print(details.value)
        return cats

class Photo(db.Model):
    date_taken = DateTimeField()
    make = TextField(null=True)
    model = TextField(null=True)
    ImageUniqueID = TextField(null=True)
    has_exif = BooleanField(null=True)
    modified = DateTimeField(default=datetime.now)
    original_height = IntegerField(null=True)
    original_width = IntegerField(null=True)
    orientation = IntegerField(null=True)
    flash_fired = IntegerField(null=True)
    image_hash = TextField(null=True)
    latitude = FloatField(null=True)
    longitude = FloatField(null=True)
    location = ForeignKeyField(rel_model=Location, related_name="photos", null=True)

    file_name = TextField(null=True)
    file_original_subpath = TextField(null=True)
    file_extension =  TextField(null=True)
    file_original_path = TextField(null=True)
    file_large_path = TextField(null=True)
    file_medium_path = TextField(null=True)
    file_thumb_path = TextField(null=True)
    file_size = IntegerField(null=True)

    Dropbox_modified = DateTimeField(null=True)
    Dropbox_revision = TextField(null=True)
    Dropbox_size = IntegerField(null=True)
    Dropbox_path =TextField(null=True)

    status = IntegerField(null=True)

    def keywords(self):
        kw = Keyword\
            .select()\
            .join(PhotoKeyword, on=PhotoKeyword.keyword)\
            .where(PhotoKeyword.photo==self)
        return kw

    def set_tags(self):

        def append_tag(category, subcategory, sortorder, value):
            try:
                kw = Keyword.get(Keyword.value==value)
            except Keyword.DoesNotExist:
                kw = Keyword.create(category=category, subcategory=subcategory, sortorder=sortorder, value=value)

            try:
                map = PhotoKeyword.get(PhotoKeyword.keyword==kw, PhotoKeyword.photo==self)
            except PhotoKeyword.DoesNotExist:
                map = PhotoKeyword.create(keyword=kw, photo=self)



        #time tags
        category = "Time"
        append_tag(category, "Years",0,self.date_taken.strftime("%Y"))
        append_tag(category, "Months",1,self.date_taken.strftime("%B"))
        append_tag(category, "Weeks", 2, "Week " + self.date_taken.strftime("%U"))
        append_tag(category, "Weekdays",3,self.date_taken.strftime("%A"))

        if 5 <= self.date_taken.hour < 12:
            append_tag(category, "Time of day",4,self.date_taken.strftime("Morning"))

        if 12 <= self.date_taken.hour < 17:
            append_tag(category, "Time of day",5,self.date_taken.strftime("Afternoon"))

        if 17 <= self.date_taken.hour < 23:
            append_tag(category, "Time of day",6,self.date_taken.strftime("Evening"))

        if 23 <= self.date_taken.hour < 5:
            append_tag(category, "Time of day",7,self.date_taken.strftime("Night"))


        category = "Camera"
        append_tag(category, "Details",0,self.model)

        append_tag(category, "Details",1,self.make)



        category = "File"
        if not self.has_exif:
            append_tag(category, "Details",0, "No Exif")

        if self.file_size <= 1024000:
            append_tag(category, "Size", 1, "Small File")

        if 1024000 < self.file_size < 3600000:
            append_tag(category, "Size", 2, "Meduim File")

        if self.file_size >= 3600000:
            append_tag(category, "Size", 3, "Large File")

        if self.location:
            category = "Places"
            if self.location.country:
                append_tag(category, "Country", 0, self.location.country)

            if self.location.state:
                append_tag(category, "State", 1, self.location.state)

            if self.location.city:
                append_tag(category, "City", 2, self.location.city)

            if self.location.suburb:
                append_tag(category, "Suburb", 3, self.location.suburb)
        else:
            append_tag(category, "Location", 4, "No Location")

class PhotoKeyword(db.Model):
    photo = ForeignKeyField(Photo)
    keyword = ForeignKeyField(Keyword)



