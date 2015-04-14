__author__ = 'hingem'


class Location():

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
        self.status = None
        self.latitude = None
        self.longitude = None
        self.location = False
        self.country = None
        self.state = None
        self.address = None
        self.road = None
        self.city = None
        self.suburb = None
        self.postcode = None

    def serialize(self):
        serial_dict ={}
        for field in self.__mongo_attributes__():
            serial_dict[field] = getattr(self, field)
        return serial_dict