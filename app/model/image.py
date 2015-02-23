import os
from datetime import datetime
from PIL import Image
from PIL import ExifTags
from app import db


class image():
    def __init__(self, imageSource):

        self.image_db = db['images']
        self.exif = self.getEXIF(imageSource)
        self.exif = None

        self.dateTaken = ""
        self.make = ""
        self.model = ""
        self.ImageUniqueID = ""
        self.path = ""
        self.hasEXIF = ""
        self.size = ""
        self.id = ""

        if isinstance(imageSource, str):
            self.imageFromFile(imageSource)
        else:
            self.imageFromDB(imageSource)



    def imageFromFile(self, imageSource):

        try:
            self.exif = self.getEXIF(imageSource)

            if self.exif == None:
                self.hasEXIF = False
                self.path = imageSource
                self.size = os.path.getsize(imageSource)
            else:
                if "DateTimeOriginal" in self.exif:
                    photoDate = str(self.exif["DateTimeOriginal"])
                elif "DateTime" in self.exif:
                    photoDate = str(self.exif["DateTime"])
                self.dateTaken = datetime.strptime(photoDate, "%Y:%m:%d %H:%M:%S")

                if "Make" in self.exif:
                    self.make = self.exif["Make"]

                if "Model" in self.exif:
                    self.model = self.exif["Model"]

                if "ImageUniqueID" in self.exif:
                    self.ImageUniqueID = self.exif["ImageUniqueID"]

                self.hasEXIF = True

        except Exception as e:
            print(e.args[0])

        self.persist()



    def imageFromDB(self, imageSource):
        self.dateTaken = imageSource['dateTaken']
        self.make = imageSource['make']
        self.model = imageSource['model']
        self.ImageUniqueID = imageSource['ImageUniqueID']
        self.path = imageSource['path']
        self.hasEXIF = imageSource['hasEXIF']
        self.size = imageSource['size']
        self.id = imageSource['_id']

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

        im_id = self.image_db.update({"dateTaken":self.dateTaken}, {"$set":imgobject}, upsert=True)



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
            return None









