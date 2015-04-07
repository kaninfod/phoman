__author__ = 'hingem'


class Location():
    status = None
    latitude = None
    longitude = None
    location = False
    country = None
    state = None
    address = None
    road = None
    db_fields = [
        "status",
        "latitude",
        "longitude",
        "location",
        "country",
        "state",
        "address",
        "road"
    ]


    def __mongo_attributes__(self):
        return [i for i in self.db_fields]

    def __mongo_populate__(self, record):
        for field in record:
                setattr(self, field, record[field])

    def __init__(self):
        pass