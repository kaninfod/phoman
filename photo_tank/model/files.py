__author__ = 'hingem'


class Files():

    filename = None
    original_subpath = None
    extension = None
    original_path = None
    large_path = None
    medium_path = None
    thumb_path = None
    size = None

    db_fields = [
        "filename",
        "extension",
        "original_subpath",
        "original_path",
        "large_path",
        "medium_path",
        "thumb_path",
        "size"
    ]


    def __mongo_attributes__(self):
        return [i for i in self.db_fields]

    def __mongo_populate__(self, record):
        for field in record:
                setattr(self, field, record[field])

    def serialize(self):
        serial_dict ={}
        for field in self.__mongo_attributes__():
            serial_dict[field] = getattr(self, field)
        return serial_dict