__author__ = 'hingem'
from pymongo import MongoClient
from bson.objectid import ObjectId


class Database(object):
    class __singleton:

        def __init__(self, host=None, port=None, db_name=None):
            self.val = None
            self.client = MongoClient(host, port)
            self.connection = self.client[db_name]

            self.images = self.connection['images']
            self.albums = self.connection['albums']

        def __str__(self):
            return self.val

        def reinitialize(self, host=None, port=None, db_name=None):
            self.__init__(host=host, port=port, db_name=db_name)

        def drop_collection(self, collection_name):
            return self.connection.drop_collection(collection_name)

        def drop_database(self, db_name):
            return self.client.drop_database(db_name)


        def save_photo(self, photo, upsert=True):
            photo.status = photo.Status.stored
            record = photo.serialize()

            if upsert:
                self.images.update({"image_hash": photo.image_hash}, {"$set": record}, upsert=True)
            else:
                self.images.insert(record)
            photo.id = str(self.images.find({"image_hash": photo.image_hash})[0]["_id"])

            return photo.id

        def get_photo_from_id(self, id):

            record = self.images.find_one({'_id': ObjectId(id), "status": {"$lt": 2}})
            return record

        def get_keywords(self):
            keywords = {}
            keywords = self.images.distinct('tags').sort("tags", 1)

            uniq = []
            dubs = []
            for x in keywords:
                if x["value"] not in uniq:
                    uniq.append(x["value"])
                else:
                    dubs.append(x)
            [keywords.remove(item) for item in dubs ]
            return keywords

        def get_keyword_categories(self):

            keywords = self.images.distinct('tags.category')
            return keywords

        def locate_image(self, field, value):

            record = self.images.find_one({field: value})
            return record


        def get_photos(self, query=None, sort_by=None, sort_direction=None):

            if sort_by:
                records = self.images.find(query, {"date_taken": 1}).sort(sort_by, 1)
            else:
                records = self.images.find(query)

            return records

        def get_dropbox_updates(self):
            query = {
                "$or": [
                    {'modified': {'$gt': "dropbox.modified"}},
                    {"dropbox.modified": None}
                ]
            }
            return self.images.find(query)

        def get_images_in_album(self, album):

            query_string = {}
            list_of_ids = []

            if album.tags_exclude or album.tags_include:
                query_string.update({
                    '$and': [
                        {'tags.value': {'$in': album.tags_include}},
                        {'tags.value': {'$nin': album.tags_exclude}}
                    ]})
                cursor = self.images.find(query_string, {"_id": 1})
                list_of_ids = [str(record['_id']) for record in cursor]
            if len(album.selected) > 0:
                list_of_ids.extend(album.selected)

            if album.startdate and album.enddate:
                query_string.update({
                    '$and': [
                        {'date_taken': {'$gte': album.startdate}},
                        {'date_taken': {'$lte': album.enddate}}
                    ]
                })

                cursor = self.images.find(query_string, {"_id": 1})
                list_of_ids = [str(record['_id']) for record in cursor]

            if not (album.startdate or album.enddate) and not (album.tags_exclude or album.tags_include) and len(
                    album.selected) == 0:
                cursor = self.images.find({}, {"_id": 1})
                ids = [str(record['_id']) for record in cursor]
                list_of_ids.extend(ids)

            album.image_count = len(list_of_ids)
            self.albums.update({"_id": album.id}, {"$set": {"image_count": album.image_count}}, upsert=False)
            return list_of_ids

        def save_album(self, album):

            alb = {
                'tags_exclude': album.tags_exclude,
                'tags_include': album.tags_include,
                'image_count': album.image_count,
                'name': album.name,
                'selected': album.selected,
                'selected_only': album.selected_only,
                'startdate': album.startdate,
                'enddate': album.enddate,
                'type': album.type
            }

            if album.id:
                self.albums.update({'_id': ObjectId(album.id)}, {"$set": alb})
            else:
                album.id = str(self.albums.insert(alb))

            return album

        def get_album(self, album_id):

            record = self.albums.find_one({"_id": ObjectId(album_id)})
            return record


        def get_albums(self):

            return self.albums.find()


        def delete_album(self, album_id, query):

            query.update({"_id": ObjectId(album_id)})
            r = self.albums.remove(query)


    instance = None

    def __new__(cls, host=None, port=None, db_name=None):
        if not Database.instance:
            Database.instance = Database.__singleton(host=host, port=port, db_name=db_name)
        return Database.instance

    def __getattr__(self, item):
        return getattr(self.instance, item)

    def __setattr__(self, key, value):
        return setattr(self.instance, key, value)