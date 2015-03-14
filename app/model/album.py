__author__ = 'martin'


from bson.objectid import ObjectId
from bson import json_util
import json

from app.model.image import image, image_query
from app import collectionsDB, imagesDB, albumsDB



class album():
    def __init__(self, id = None):
        self.tags_include = ""
        self.tags_exclude = ""
        self.name = ""
        self.id = id
        self.imagecount = ""
        self.cursor = ""

        if id:
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
        elif isinstance(index,slice):
            lst = list()
            self.cursor.rewind()
            for item in self.cursor[index.start:index.stop]:
                 lst.append(image(item))
            return lst

    def _get_collection(self):
        if self.id:
            self.album = albumsDB.find_one({"_id":ObjectId(self.id)})
            if self.album:
                self.id = self.album["_id"]
                self.name = self.album["name"]

                for field in self.album["query"]:
                    setattr(self.query, field, self.album["query"][field])

                self._get_images()


    def _save(self):
        if self.name and self.query:

            self.album = albumsDB.find_one({"query.query":self.query.query})
            if self.album:
                self.id = self.album["_id"]
                albumsDB.update({"_id":self.id}, {"$set":self._serialize()})
            else:
                id = albumsDB.insert(self._serialize())
                self.id = id
                self.album = albumsDB.find_one({"_id":self.id})

            self._get_images()

    def _get_images(self):

        query_string = {}

        if self.tags_include:
            query_string.update(
                {'db_tags':
                     {
                         '$all': self.tags_include,
                         '$nin': self.tags_exclude
                     }
                })
            self.cursor = imagesDB.find((query_string))

            self.imagecount = self.cursor.count()
            #i = albumsDB.update({"_id":self.id}, {"$set":{"imagecount":self.imagecount}}, upsert=False)


    def save(self):
        alb = {
            'tags_exclude':self.tags_exclude,
            'tags_include':self.tags_include,
            'image_count':self.imagecount,
            'name':self.name
        }

        self.album = albumsDB.find_one({'name':self.name})
        if self.album:
            albumsDB.update(alb)
        else:
            self.id = str(albumsDB.insert(alb))
            print()