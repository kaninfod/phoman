__author__ = 'martin'

from app.model.image import image
from app import db
from math import ceil
from datetime import datetime
import json
from bson import json_util
from bson.objectid import ObjectId


class imageCollection():
    def __init__(self, query="", name="", saveToDB=False, id = None):

        self.image_db = db['images']
        self.collection_db = db['collections']
        self.query = query
        self.name = name
        self.id = id

        if saveToDB and query:
            if not name:
                self.name = "Created %s" % datetime.now()
            t = self.getDBObj()
            self.id = self.collection_db.insert(t)


        elif self.id:
            self.collection = self.collection_db.find_one({"_id":ObjectId(self.id)})
            self.query = json.loads(self.collection["query"])
            self.name = self.collection["name"]

        self.cursor = self.image_db.find(self.query)

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

    def getDBObj(self):
        collection = {
            "name" : self.name,
            "query" : json.dumps(self.query, default=json_util.default),
        }

        return collection

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
