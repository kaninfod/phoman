import os
from datetime import datetime
from PIL import Image
from PIL import ExifTags
from app import db


class image():
    def __init__(self, fileName):

        self.DBCollection = db['images']
        self.exif = self.getEXIF(fileName)
        self.dateTaken = ""
        self.make = ""
        self.model = ""
        self.ImageUniqueID = ""
        self.path = ""
        self.hasEXIF = ""
        self.size = ""

        try:
            photoDate = str(self.exif["DateTimeOriginal"])
            self.dateTaken = datetime.strptime(photoDate, "%Y:%m:%d %H:%M:%S")
            self.make = self.exif["Make"]
            self.model = self.exif["Model"]
            self.path = fileName
            self.hasEXIF = True
            self.size = os.path.getsize(fileName)
            self.ImageUniqueID = self.exif["ImageUniqueID"]

        except Exception as e:
            print(e.args[0])

        self.persist()


    def persist(self):
        imgobject = {
            "dateTaken" : self.dateTaken,
            "make" : self.make,
            "model" : self.model,
            "ImageUniqueID" : self.ImageUniqueID,
            "path" : self.path,
            "hasEXIF" : self.hasEXIF,
            "size" : self.size
        }
        self.checkIfExists()
        im_id = self.DBCollection.update({"dateTaken":self.dateTaken}, {"$set":imgobject}, upsert=True)
        #im_id = self.DBCollection.insert(imgobject)
        print()

    def checkIfExists(self):
        id = self.DBCollection.find_one({"dateTaken":self.dateTaken})
        print()



    def getEXIF(self, file):

        try:
            imgFile=Image.open(file,'r')
            exif = {
                ExifTags.TAGS[k]: v
                for k, v in imgFile._getexif().items()
                if k in ExifTags.TAGS
            }
            return exif
        except Exception as e:
            print(e.args[0])













# from app import db
#
# from PIL import Image
# from PIL import ExifTags
# from datetime import datetime
# import os
#
#
#
# class image(db.Document):
#     id = db.UUIDField()
#     dateTaken = db.DateTimeField(required=False, unique=True)
#     make = db.StringField()
#     model = db.StringField()
#     ImageUniqueID = db.StringField()
#     path = db.StringField()
#     hasEXIF = db.BooleanField(required=True)
#     size = db.IntField()
#
#
#     def update(self, fileName):
#
#         exif = self.getEXIF(fileName)
#         try:
#             img = image()
#             photoDate = str(exif["DateTimeOriginal"])
#             self.dateTaken = datetime.strptime(photoDate, "%Y:%m:%d %H:%M:%S")
#             self.make = exif["Make"]
#             self.model = exif["Model"]
#             self.path = fileName
#             self.hasEXIF = True
#             self.size = os.path.getsize(fileName)
#             self.ImageUniqueID = exif["ImageUniqueID"]
#             self.save()
#         except Exception as e:
#             print(e.args[0])
#
#
#
#
#
#     def getEXIF(self, file):
#
#         try:
#             imgFile=Image.open(file,'r')
#             exif = {
#                 ExifTags.TAGS[k]: v
#                 for k, v in imgFile._getexif().items()
#                 if k in ExifTags.TAGS
#             }
#             return exif
#         except Exception as e:
#             print(e.args[0])