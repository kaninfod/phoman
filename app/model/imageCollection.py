__author__ = 'martin'

import datetime

from bson.objectid import ObjectId
from bson import json_util
import json

from app.model.image import image, ImageQuery
from app import collectionsDB, imagesDB


class imageCollection():
    def __init__(self, collection_id=None):
        self.query = ImageQuery()  # query()
        self.name = ""
        self.id = collection_id
        self.imagecount = ""
        self.cursor = ""

        if collection_id:
            self._get_collection()

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
        elif isinstance(index, slice):
            lst = list()
            self.cursor.rewind()
            for item in self.cursor[index.start:index.stop]:
                lst.append(image(item))
            return lst

    def _get_collection(self):
        if self.id:
            self.collection = collectionsDB.find_one({"_id": ObjectId(self.id)})
            if self.collection:
                self.id = self.collection["_id"]
                self.name = self.collection["name"]

                for field in self.collection["query"]:
                    setattr(self.query, field, self.collection["query"][field])

                self._get_images()


    def _save(self):
        if self.name and self.query:

            self.collection = collectionsDB.find_one({"query.query": self.query.query})
            if self.collection:
                self.id = self.collection["_id"]
                collectionsDB.update({"_id": self.id}, {"$set": self._serialize()})
            else:
                id = collectionsDB.insert(self._serialize())
                self.id = id
                self.collection = collectionsDB.find_one({"_id": self.id})

            self._get_images()

    def _get_images(self):
        if self.id:
            self.cursor = imagesDB.find(self.query._query)
            self.imagecount = self.cursor.count()
            i = collectionsDB.update({"_id": self.id}, {"$set": {"imagecount": self.imagecount}}, upsert=False)

    def _serialize(self):
        collection = {
            "name": self.name,
            "imagecount": self.imagecount,
            "query": self.query.serialize(),
        }

        return collection


    def serialize(self):
        return json.dumps(self.__dict__, default=json_util.default)
