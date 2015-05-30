from peewee import *
from phototank.app import db

from datetime import datetime


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
    location = ForeignKeyField(rel_model=Location, related_name="photos")

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

            m = PhotoKeyword.create(keyword=kw, photo=self)



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


        category = "Places"
        if self.location.country:
            append_tag(category, "Country", 0, self.location.country)

        if self.location.state:
            append_tag(category, "State", 1, self.location.state)

        if self.location.city:
            append_tag(category, "City", 2, self.location.city)

        if self.location.suburb:
            append_tag(category, "Suburb", 3, self.location.suburb)

        if not self.location.status == 1:
            append_tag(category, "Location", 4, "No Location")

class PhotoKeyword(db.Model):
    photo = ForeignKeyField(Photo)
    keyword = ForeignKeyField(Keyword)

for table in [Photo, Location, Keyword, PhotoKeyword]:
    try:
        table.create_table()
    except Exception as e:
        print(e)

