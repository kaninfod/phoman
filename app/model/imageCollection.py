__author__ = 'martin'

from math import ceil
import datetime

from bson.objectid import ObjectId

from app.model.image import image
from app import collectionsDB, imagesDB
from app import ImagePersistedFields


class imageCollection():
    def __init__(self, id = None):
        self.query = query()
        self.name = ""
        self.id = id
        self.imagecount = ""
        self.cursor = None

        if id:
            self.getCollection()

    def __iter__(self):
        return self

    def __next__(self):

        if self.cursor and self.cursor.alive:
            return image(next(self.cursor))
        else:
            raise StopIteration()

    def __getitem__(self, index):
        if isinstance(index, int):
            return image(self.cursor[index])
        elif isinstance(index,slice):
            lst = list()
            self.cursor.rewind()
            for item in self.cursor[index.start:index.stop]:
                 lst.append(image(item))
            return lst

    def getCollection(self):
        if self.id:
            self.collection = self.collection = collectionsDB.find_one({"_id":ObjectId(self.id)})
            if self.collection:
                self.id = self.collection["_id"]
                self.name = self.collection["name"]
                self.query.setFromDB(self.collection["query"])
                self.getImages()


    def save(self):
        if self.name and self.query:
            qry = self.query.queryFetchImages()
            i = collectionsDB.update({"query":self.query.serialize()}, {"$set":self.getDBObj()}, upsert=True)
            self.collection = collectionsDB.find_one({"query":self.query.serialize()})
            self.id = self.collection["_id"]
            self.getImages()

    def getImages(self):
        if self.id:
            self.cursor = imagesDB.find((self.query.queryFetchImages()))
            self.imagecount = self.cursor.count()
            i = collectionsDB.update({"_id":self.id}, {"$set":{"imagecount":self.imagecount}}, upsert=False)

    def getDBObj(self):
        collection = {
            "name" : self.name,
            "imagecount": self.imagecount,
            "query" : self.query.serialize(),
        }

        return collection


class query():

    def __init__(self):
        for field in ImagePersistedFields:
            setattr(self,field,None)
        self._dateTaken_gt = None
        self._dateTaken_lt = None


    @property
    def dateTaken_gt(self):
        return self._dateTaken_gt

    @dateTaken_gt.setter
    def dateTaken_gt(self, value):
        if isinstance(value, datetime.date):
            self._dateTaken_gt = datetime.datetime.combine(value, datetime.time.min)


    @property
    def dateTaken_lt(self):
        return self._dateTaken_lt

    @dateTaken_lt.setter
    def dateTaken_lt(self, value):
        if isinstance(value, datetime.date):
            self._dateTaken_lt = datetime.datetime.combine(value, datetime.time.min)



    def queryFetchImages(self):
        qry = {}

        for field in ImagePersistedFields:
            if getattr(self,field):
                qry[field] = getattr(self,field)

        if self.dateTaken_gt:

            if "dateTaken" in qry:
                qry["dateTaken"]["$gte"] = self.dateTaken_gt
            else:
                qry["dateTaken"] = {"$gte":self.dateTaken_gt}

        if self.dateTaken_lt:

            if "dateTaken" in qry:
                qry["dateTaken"]["$lt"] = self.dateTaken_lt
            else:
                qry["dateTaken"] = {"$lt":self.dateTaken_lt}

        return qry

    def setFromDB(self, DBObject):
        for field in DBObject:
            if field in DBObject:
                setattr(self,field,DBObject[field])

    def serialize(self):
        obj = self.__dict__.copy()
        if "_dateTaken_lt" in obj:
            obj["dateTaken_lt"] = obj.pop("_dateTaken_lt")
        if "_dateTaken_gt" in obj:
            obj["dateTaken_gt"] = obj.pop("_dateTaken_gt")
        return obj

class paginateor():
    def __init__(self, perPage, totalCount, page):
        self.perPage = perPage
        self.totalCount = totalCount
        self.page = page


    def pages(self):
        return int(ceil(self.totalCount / float(self.perPage)))

    def has_prev(self):
        return self.page > 1

    def has_next(self):
        return self.page < self.pages


    def iterPages(self):
        for num in range(1, self.pages + 1):
            yield num
