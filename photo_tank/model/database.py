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
            self.keywords = self.connection['keywords']

        def __str__(self):
            return self.val

        def reinitialize(self, host=None, port=None, db_name=None):
            self.__init__(host=host, port=port, db_name=db_name)

        def drop_collection(self, collection_name):
            return self.connection.drop_collection(collection_name)

        def drop_database(self, db_name):
            return self.client.drop_database(db_name)

        def initialize_db(self):
            from pymongo import ASCENDING, DESCENDING
            collections = self.connection.collection_names()
            if not "keywords" in collections:
                self.connection.create_collection("keywords")
            self.keywords.create_index( { "keywords": 1 }, { "unique": True } )


        def create_keyword(self, keyword):

            try:
                result = self.keywords.update({"value":keyword["value"]},{"$set": keyword}, upsert=True)
                keyword_id = self.keywords.find({"value":keyword["value"]})
                if keyword_id:
                    return keyword_id[0]["_id"]
                else:
                    return 0

            except Exception as e:
                print(e)



        def save_photo(self, photo, upsert=True):
            photo.status = photo.Status.stored
            record = photo.serialize()

            if upsert:
                res = self.images.update({"image_hash": photo.image_hash}, {"$set": record}, upsert=True)
            else:
                self.images.insert(record)
            photo.id = str(self.images.find({"image_hash": photo.image_hash})[0]["_id"])

            return photo.id

        def get_photo_from_id(self, id):

            record = self.images.find_one({'_id': ObjectId(id), "status": {"$lt": 2}})
            return record

        def get_keywords(self):

            keywords = self.keywords.find({}).sort("category", 1)

            return keywords


        def get_keyword_categories(self):

            keywords = self.keywords.distinct('category')
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

        def image_count(self, album):
            if album.selected or album.tags_exclude or album.tags_include or album.startdate or album.enddate:

                query_string = {
                    '$or': [
                        {'_id': {'$in': album.selected}},

                        {'$and': [
                            {'tags': {'$in': album.tags_include}},
                            {'tags': {'$nin': album.tags_exclude}}
                        ]},
                        {'$and': [
                            {'date_taken': {'$gte': album.startdate}},
                            {'date_taken': {'$lte': album.enddate}}
                        ]}
                    ]
                }
            else:
                query_string = {    }
            return self.images.find(query_string).count()


        def get_images_in_album(self, album, skip=0, limit=0):
            if album.selected or album.tags_exclude or album.tags_include or album.startdate or album.enddate:
                query_string = {
                    '$or': [
                        {'_id': {'$in': album.selected}},

                        {'$and': [
                            {'tags': {'$in': album.tags_include}},
                            {'tags': {'$nin': album.tags_exclude}}
                        ]},
                        {'$and': [
                            {'date_taken': {'$gte': album.startdate}},
                            {'date_taken': {'$lte': album.enddate}}
                        ]}
                    ]
                }
            else:
                query_string = {    }
            cursor = self.images.find(query_string).sort("date_taken", 1).skip(skip).limit(limit)
            album._image_count = cursor.count()
            self.albums.update({"_id": album.id}, {"$set": {"image_count": album._image_count}}, upsert=False)
            return cursor

        def album_cur(self, id):
            cur = self.images.find()
            return cur

        def save_album(self, album):
            exclude = [ObjectId(_id) for _id in album.tags_exclude]
            include = [ObjectId(_id) for _id in album.tags_include]
            alb = {
                'tags_exclude': exclude,
                'tags_include': include,
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