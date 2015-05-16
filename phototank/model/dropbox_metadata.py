__author__ = 'hingem'


class DropboxMetadata():

    db_fields = [
        "modified",
        "revision",
        "size",
        "path"
    ]


    def __mongo_attributes__(self):
        return [i for i in self.db_fields]

    def populate(self, record):
        for field in record:
            setattr(self, field, record[field])

    def __init__(self):
        self.modified = None
        self.revision = None
        self.size = None
        self.path = False


    def serialize(self):
        serial_dict ={}
        for field in [i for i in self.db_fields]:
            serial_dict[field] = getattr(self, field)
        return serial_dict