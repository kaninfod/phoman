__author__ = 'martin'

from app.model.image import image
from app import db
from app import collectionsDB, imagesDB
from math import ceil
from bson.objectid import ObjectId
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
            qry = self.query.getDBObj()
            i = collectionsDB.update({"query":qry}, {"$set":self.getDBObj()}, upsert=True)
            self.collection = collectionsDB.find_one({"query":qry})
            self.id = self.collection["_id"]
            self.getImages()

    def getImages(self):
        if self.id:
            self.cursor = imagesDB.find(self.query.getDBObj())
            self.imagecount = self.cursor.count()

    def getDBObj(self):
        collection = {
            "name" : self.name,
            "query" : self.query.getDBObj(),
        }

        return collection


class query():

    def __init__(self):
        for field in ImagePersistedFields:
            setattr(self,field,None)


    def getDBObj(self):
        qry = {}
        for field in ImagePersistedFields:
            if getattr(self,field):
                qry[field] = getattr(self,field)
        return qry

    def setFromDB(self, DBObject):
        for field in ImagePersistedFields:
            if field in DBObject:
                setattr(self,field,DBObject[field])


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
