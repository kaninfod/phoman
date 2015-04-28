
from photo_tank.model.location import Location
from photo_tank.model.files import Files
from photo_tank.model.database import Database
from photo_tank.model.dropbox_metadata import DropboxMetadata
from datetime import datetime
import os
from enum import Enum

class Photo():

    db_fields = [
        "make",
        "model",
        "ImageUniqueID",
        "has_exif",
        "id",
        "modified",
        "date_taken",
        "original_height",
        "original_width",
        "orientation",
        "flash_fired",
        "location",
        "image_hash",
        "links",
        "tags",
        "files",
        "dropbox",
        "status"
    ]

    class Status(Enum):
        stored = 1
        invisible = 2
        deleted = 3
        unknown = 4

    def __init__(self, image_source=None, image_id=None, update_location=False):
        self.make = None
        self.model = None
        self.ImageUniqueID = None
        self.has_exif = None
        self.id = None
        self.modified = None
        self.date_taken = None
        self.original_height = None
        self.original_width = None
        self.orientation = None
        self.flash_fired = None
        self.image_hash = None
        self.status = Photo.Status.unknown
        self.links = {}
        self.tags = []
        self.location = Location()
        self.files = Files()
        self.db = Database()
        self.dropbox = DropboxMetadata()


        if image_id:
            self.populate(self.db.get_photo_from_id(image_id))

        elif isinstance(image_source, dict):
                self.populate(image_source)

    def set_attributes(self):
        return [i for i in self.db_fields]

    def save(self):
        self.db.save_photo(self)

    def populate(self, record):
        if record:
            for field in record:

                if field == "_id":
                    setattr(self, "id", str(record["_id"]))

                elif field == "location":
                    self.location.populate(record[field])

                elif field == "files":
                    self.files.populate(record[field])

                elif field == "dropbox":
                    self.dropbox.populate(record[field])

                elif field == "status":
                    setattr(self, field, self.Status(record[field]))

                else:
                    setattr(self, field, record[field])

    def serialize(self):
        serial_dict ={}
        for field in [i for i in self.db_fields]:

            if field == "location":
                serial_dict[field] = self.location.serialize()

            elif field == "files":
                serial_dict[field] = self.files.serialize()

            elif field == "dropbox":
                serial_dict[field] = self.dropbox.serialize()

            elif field == "modified":
                serial_dict["modified"] = datetime.utcnow()

            elif field == "status":
                serial_dict["status"] = self.status.value

            elif not field == "id":
                serial_dict[field] = getattr(self, field)

        return serial_dict

    def add_link(self, ref, type):
        self.links.update(
            {
                "ref": ref,
                "type": type
            }

        )

    def set_tags(self):

        def append_tag(category, subcategory, sortorder, value):
            keyword = {
                "value": value,
                "category": category,
                "subcategory": subcategory,
                "sortorder": sortorder
            }
            keyword_id = self.db.create_keyword(keyword)
            self.tags.append(keyword_id)
            #self.tags.append({"category": category,"subcategory": subcategory,"sortorder": sortorder, "value": value})

        self.tags = []

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

        if self.files.size <= 1024000:
            append_tag(category, "Size", 1, "Small File")

        if 1024000 < self.files.size < 3600000:
            append_tag(category, "Size", 2, "Meduim File")

        if self.files.size >= 3600000:
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



    def delete(self):

        #delete in webimages
        os.remove(self.files.thumb_path)
        os.remove(self.files.medium_path)
        os.remove(self.files.large_path)
        #delete original
        os.remove(self.files.original_path)
        #delete in dropbox

        #delete in db
        self.status = self.Status.deleted

        #clean up empty folders

        self.save()

    def invisible(self, state):

        self.status = self.Status.invisible
        self.save()

    def __str__(self):
        return self.original_path



    def __del__(self):
        pass