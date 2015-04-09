
from photo_tank.model.location import Location
from photo_tank.model.files import Files
from photo_tank.model.database import Database

class Photo():



    make = None
    model = None
    ImageUniqueID = None
    has_exif = None
    id = None
    date_taken = None
    original_height = None
    original_width = None
    orientation = None
    flash_fired = None
    tags = []
    image_hash = None
    links = {}
    location = Location
    files = Files


    db_fields = [
        "make",
        "model",
        "ImageUniqueID",
        "has_exif",
        "id",
        "date_taken",
        "original_height",
        "original_width",
        "orientation",
        "flash_fired",
        "location",
        "image_hash",
        "links",
        "tags",
        "files"
    ]

    def __init__(self, image_source=None, image_id=None, update_location=False):
        self.tags = []
        self.location = Location()
        self.files = Files()
        self.db = Database()

        if image_id:
            self.__mongo_populate__(self.db.get_image_from_id(image_id))

        else:
            if isinstance(image_source, str):
                return
                #self._image_from_file(image_source)

            elif isinstance(image_source, dict):
                self.__mongo_populate__(image_source)


    def __mongo_attributes__(self):
        return [i for i in self.db_fields]

    def __mongo_save__(self):
        self.db.save_image(self)

    def __mongo_populate__(self, record):

        for field in record:
            if field == "_id":
                setattr(self, "id", str(record["_id"]))
            elif field == "location":
                self.location.__mongo_populate__(record[field])
            elif field == "files":
                self.files.__mongo_populate__(record[field])

            else:
                setattr(self, field, record[field])


    def add_link(self, ref, type):
        self.links.update(
            {
                "ref": ref,
                "type": type
            }

        )


    def set_tags(self):

        self.tags = []

        #time tags
        category = "Time"
        self.tags.append({"category": category, "value": self.date_taken.strftime("%B")})
        self.tags.append({"category": category, "value":  self.date_taken.strftime("%Y")})
        self.tags.append({"category": category, "value":  self.date_taken.strftime("%A")})
        self.tags.append({"category": category, "value":  "Week " + self.date_taken.strftime("%U")})

        if 5 <= self.date_taken.hour < 12:
            self.tags.append({"category": category, "value": "Morning"})
        if 12 <= self.date_taken.hour < 17:
            self.tags.append({"category": category, "value": "Afternoon"})
        if 17 <= self.date_taken.hour < 23:
            self.tags.append({"category": category, "value":  "Evening"})
        if 23 <= self.date_taken.hour < 5:
            self.tags.append({"category": category, "value":  "Night"})

        category = "Camera"
        self.tags.append({"category": category, "value":  self.model})
        self.tags.append({"category": category, "value":  self.make})


        category = "File"
        if not self.has_exif:
            self.tags.append({"category": category, "value":  "No EXIF"})

        if self.files.size <= 1024000:
            self.tags.append({"category": category, "value":  "Small file"})
        if 1024000 < self.files.size < 3600000:
            self.tags.append({"category": category, "value":  "Medium file"})
        if self.files.size >= 3600000:
            self.tags.append({"category": category, "value":  "Large file"})

        category = "Location"
        if self.location.country:
            self.tags.append({"category": category, "value":  self.location.country})
        if self.location.state:
            self.tags.append({"category": category, "value":  self.location.state})
        if not self.location.status == 1:
            self.tags.append({"category": category, "value":  "No Location"})

    def __str__(self):
        return self.original_path



