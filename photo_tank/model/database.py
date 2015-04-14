__author__ = 'hingem'
from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime




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
            self.__init__(host=host,port=port,db_name=db_name)

        def drop_collection(self, collection_name):
            return self.connection.drop_collection(collection_name)

        def drop_database(self, db_name):
            return self.client.drop_database(db_name)


        def save_image(self, image, upsert=True):

            imgobject = {}

            for field in image.__mongo_attributes__():
                if field == "location":
                    imgobject[field] = image.location.serialize()
                elif field == "files":
                    imgobject[field] = image.files.serialize()
                elif field == "dropbox":
                    imgobject[field] = image.dropbox.serialize()
                elif not field == "id":
                    imgobject[field] = getattr(image, field)

            imgobject["modified"] = datetime.datetime.utcnow()

            if upsert:
                self.images.update({"image_hash": image.image_hash}, {"$set": imgobject}, upsert=True)
            else:
                self.images.insert(imgobject)
            image.id = str(self.images.find({"image_hash":image.image_hash})[0]["_id"])
            return image.id

        def get_image_from_id(self, id):

            record = self.images.find_one({'_id': ObjectId(id)})
            return record

        def get_keywords(self):

            keywords = self.images.distinct('tags')
            return keywords

        def get_keyword_categories(self):

            keywords = self.images.distinct('tags.category')
            return keywords



        def locate_image(self, field, value):

            record = self.images.find_one({field: value})
            return record


        def get_images(self, query=None, sort_by=None, sort_direction=None):

            if sort_by:
                records = self.images.find(query, {"date_taken":1}).sort(sort_by,1)
            else:
                records = self.images.find(query)

            return records

        def get_dropbox_updates(self):
            query = {
                "$or":[
                    {'modified':{'$gt':"dropbox.modified"}},
                    {"dropbox.modified":None}
                ]
            }
            return self.images.find(query)


        def get_images_in_album(self,album):

            query_string = {}
            list_of_ids = []

            if album.tags_exclude or album.tags_include:
                query_string.update({
                    '$and':[
                        {'tags.value':{'$in':album.tags_include}},
                        {'tags.value':{'$nin':album.tags_exclude}}
                    ]})
                cursor = self.images.find(query_string, {"_id":1} )
                list_of_ids = [str(record['_id']) for record in cursor]
            if len(album.selected) > 0:
                list_of_ids.append(album.selected)



            if album.startdate and album.enddate:
                query_string.update({
                    '$and':[
                            {'date_taken':{'$gte':album.startdate}},
                            {'date_taken':{'$lte':album.enddate}}
                            ]
                    })

                cursor = self.images.find(query_string, {"_id":1} )
                list_of_ids = [str(record['_id']) for record in cursor]

            if not (album.startdate or album.enddate) and not (album.tags_exclude or album.tags_include) and len(album.selected) == 0:
                cursor = self.images.find({}, {"_id":1} )
                ids = [str(record['_id']) for record in cursor]
                list_of_ids.extend(ids)
                #list_of_ids.append(ids)

            album.image_count = len(list_of_ids)
            self.albums.update({"_id": album.id}, {"$set": {"image_count": album.image_count}}, upsert=False)
            return list_of_ids


                # if album.tags_exclude or album.tags_include and not album.selected_only:
                #     query_string.update({
                #         '$and':[
                #             {'tags.value':{'$in':album.tags_include}},
                #             {'tags.value':{'$nin':album.tags_exclude}}
                #         ]})
                #
                #     cursor = imagesDB.find(query_string, {"_id":1} )
                #     list_of_ids = [str(record['_id']) for record in cursor]
                #
                # elif not album.selected_only:
                #     cursor = imagesDB.find({}, {"_id":1} )
                #     list_of_ids = [str(record['_id']) for record in cursor]
                # elif album.selected_only:
                #     list_of_ids = album.selected



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

            query.update({"_id":ObjectId(album_id)})
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