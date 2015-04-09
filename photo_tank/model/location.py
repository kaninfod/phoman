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
    city = None
    suburb = None
    postcode = None
    db_fields = [
        "status",
        "latitude",
        "longitude",
        "location",
        "country",
        "city",
        "suburb",
        "postcode",
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

    def serialize(self):
        serial_dict ={}
        for field in self.__mongo_attributes__():
            serial_dict[field] = getattr(self, field)
        return serial_dict