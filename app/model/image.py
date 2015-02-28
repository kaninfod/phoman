import os
from datetime import datetime
from PIL import Image
from PIL import ExifTags
from app import imagesDB
from app import ImagePersistedFields

class image():
    def __init__(self, imageSource):

        self.exif = self.getEXIF(imageSource)
        self.exif = None

        for field in ImagePersistedFields:
            setattr(self,field,None)


        if isinstance(imageSource, str):
            self.imageFromFile(imageSource)
        else:
            self.imageFromDB(imageSource)



    def imageFromFile(self, imageSource):

        try:
            self.exif = self.getEXIF(imageSource)

            if self.exif == None:
                self.hasEXIF = False
            else:
                if "DateTimeOriginal" in self.exif:
                    photoDate = str(self.exif["DateTimeOriginal"])
                elif "DateTime" in self.exif:
                    photoDate = str(self.exif["DateTime"])
                self.dateTaken = datetime.strptime(photoDate, "%Y:%m:%d %H:%M:%S")
                self.year = self.dateTaken.year
                self.month = self.dateTaken.month
                self.day = self.dateTaken.day

                if "Make" in self.exif:
                    self.make = self.exif["Make"]

                if "Model" in self.exif:
                    self.model = self.exif["Model"]

                if "ImageUniqueID" in self.exif:
                    self.ImageUniqueID = self.exif["ImageUniqueID"]

                self.hasEXIF = True
                self.path = imageSource
                self.size = os.path.getsize(imageSource)
        except Exception as e:
            print(e.args[0])

        self.persist()



    def imageFromDB(self, imageSource):

        for field in ImagePersistedFields:
            if field == "id":
                setattr(self,field,imageSource['_id'])
            else:
                setattr(self,field,imageSource[field])

    def persist(self):
        imgobject = {}
        for field in ImagePersistedFields:
            if field !='id':
                imgobject[field] = getattr(self,field)
        im_id = imagesDB.update({"dateTaken":self.dateTaken}, {"$set":imgobject}, upsert=True)



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

    def __str__(self):

        return self.path

