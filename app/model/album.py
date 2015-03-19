__author__ = 'martin'

from bson.objectid import ObjectId

from app.model.image import image
from app import imagesDB, albumsDB


class Album():
    def __init__(self, album_id=None):
        self.tags_include = []
        self.tags_exclude = []
        self.name = ""
        self.id = album_id
        self.imagecount = ""
        self.cursor = ""
        self._paginator = None
        self._position = 0

        if album_id:
            self._get_collection()


    @property
    def paginator(self):
        return self._paginator

    @paginator.setter
    def paginator(self, paginator):
        self.cursor.skip(paginator.min_rec)
        self._position = paginator.min_rec
        self._paginator = paginator


    def __iter__(self):
        return self

    def __next__(self):

        if self.cursor and self.cursor.alive:
            if self._paginator:
                if self._position < self.paginator.max_rec:
                    self._position += 1
                    return image(next(self.cursor))
                else:
                    #self.position = 0
                    raise StopIteration()
            else:
                return image(next(self.cursor))
        else:

            raise StopIteration()

    def __getitem__(self, index):

        if isinstance(index, int):
            return image(self.cursor[index])
        elif isinstance(index, slice):
            return self.cursor[index.start:index.stop]
            # lst = list()
            # self.cursor.rewind()
            # for item in self.cursor[index.start:index.stop]:
            #     lst.append(image(item))
            # return lst

    def _get_collection(self):
        if self.id:
            self.album = albumsDB.find_one({"_id": ObjectId(self.id)})
            if self.album:
                self.id = self.album["_id"]
                self.name = self.album["name"]
                self.tags_exclude = self.album["tags_exclude"]
                self.tags_include = self.album["tags_include"]

                self._get_images()


    def _get_images(self):






        #
        # if self.tags_include:
        #     query_string.update(
        #         {'db_tags':
        #              {
        #                  '$all': self.tags_include
        #              }
        #          })
        #
        # if self.tags_exclude:
        #     query_string.update(
        #         {'db_tags':
        #              {
        #                  '$nin': self.tags_exclude
        #              }
        #          })
        query_string = {}
        if self.tags_exclude or self.tags_include:
            query_string.update({
                '$and':[
                    {'db_tags':{'$in':self.tags_include}},
                    {'db_tags':{'$nin':self.tags_exclude}}
                ]})


        self.cursor = imagesDB.find(query_string)
        self.imagecount = self.cursor.count()
        albumsDB.update({"_id": self.id}, {"$set": {"imagecount": self.imagecount}}, upsert=False)


    def save(self):
        alb = {
            'tags_exclude': self.tags_exclude,
            'tags_include': self.tags_include,
            'image_count': self.imagecount,
            'name': self.name
        }

        if self.id:
            albumsDB.update({'_id': ObjectId(self.id)}, {"$set": alb})
        else:
            self.id = str(albumsDB.insert(alb))
        self._get_images()
