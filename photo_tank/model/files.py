__author__ = 'hingem'


class Files():



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
    def __init__(self):
        self.filename = None
        self.original_subpath = None
        self.extension = None
        self.original_path = None
        self.large_path = None
        self.medium_path = None
        self.thumb_path = None
        self.size = None

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