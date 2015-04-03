from app.model.mongo_db import get_image_from_id, save_image


class image():
    db_filename = None
    db_original_subpath = None
    db_original_path = None
    db_large_path = None
    db_medium_path = None
    db_thumb_path = None
    db_size = None
    db_make = None
    db_model = None
    db_ImageUniqueID = None
    db_has_exif = None
    db_id = None
    db_date_taken = None
    db_latitude = None
    db_longitude = None
    db_original_height = None
    db_original_width = None
    db_orientation = None
    db_flash_fired = None
    db_tags = []
    db_location = False
    db_country = None
    db_state = None
    db_address = None
    db_road = None
    db_image_hash = None
    db_extension = None
    db_links = {}


    def __mongo_attributes__(self):

        return [i for i in dir(self) if i.startswith('db_')]

    def __mongo_save__(self):
        save_image(self)



    def __mongo_populate__(self, record):

        for field in record:
            if field == "_id":
                setattr(self, "db_id", str(record["_id"]))
            elif "db_" in field:
                setattr(self, field, record[field])



    def __init__(self, image_source=None, image_id=None, update_location=False):
        self.db_tags = []

        if image_id:
            self.__mongo_populate__(get_image_from_id(image_id))

        else:
            if isinstance(image_source, str):
                return
                #self._image_from_file(image_source)

            elif isinstance(image_source, dict):
                self.__mongo_populate__(image_source)
                #if update_location:
                #    lookup_location(self)

    def add_link(self, ref, type):
        self.db_links.update(
            {
                "ref": ref,
                "type": type
            }

        )


    def set_tags(self):

        self.db_tags = []

        #time tags
        category = "Time"
        self.db_tags.append({"category": category, "value": self.db_date_taken.strftime("%B")})
        self.db_tags.append({"category": category, "value":  self.db_date_taken.strftime("%Y")})
        self.db_tags.append({"category": category, "value":  self.db_date_taken.strftime("%A")})
        self.db_tags.append({"category": category, "value":  "Week " + self.db_date_taken.strftime("%U")})

        if 5 <= self.db_date_taken.hour < 12:
            self.db_tags.append({"category": category, "value": "Morning"})
        if 12 <= self.db_date_taken.hour < 17:
            self.db_tags.append({"category": category, "value": "Afternoon"})
        if 17 <= self.db_date_taken.hour < 23:
            self.db_tags.append({"category": category, "value":  "Evening"})
        if 23 <= self.db_date_taken.hour < 5:
            self.db_tags.append({"category": category, "value":  "Night"})

        category = "Camera"
        self.db_tags.append({"category": category, "value":  self.db_model})
        self.db_tags.append({"category": category, "value":  self.db_make})


        category = "File"
        if not self.db_has_exif:
            self.db_tags.append({"category": category, "value":  "No EXIF"})

        if self.db_size <= 1024000:
            self.db_tags.append({"category": category, "value":  "Small file"})
        if 1024000 < self.db_size < 3600000:
            self.db_tags.append({"category": category, "value":  "Medium file"})
        if self.db_size >= 3600000:
            self.db_tags.append({"category": category, "value":  "Large file"})


        category = "Location"
        if self.db_country:
            self.db_tags.append({"category": category, "value":  self.db_country})

        if self.db_state:
            self.db_tags.append({"category": category, "value":  self.db_state})

        if not self.db_location:
            self.db_tags.append({"category": category, "value":  "No Location"})




    def __str__(self):
        return self.db_original_subpath



