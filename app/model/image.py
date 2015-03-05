import os, errno
from bson.objectid import ObjectId
from datetime import datetime
from PIL import Image, ImageOps
from PIL import ExifTags
from app import imagesDB
from app import ImagePersistedFields
from app import *

class image():
    def __init__(self, imageSource=None, id=None):


        self.exif = None

        for field in ImagePersistedFields:
            setattr(self,field,None)

        self.filename = ""
        self.originalPath = ""
        self.largePath = ""
        self.mediumPath = ""
        self.thumbPath = ""


        if id:
            imageSource = imagesDB.find_one({'_id':ObjectId(id)})

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

                self.originalPath = imageSource
                self.filename  = os.path.split(imageSource)[1]

                webimages_path = app.config["IMAGE_THUMBS"] + self.originalPath.replace(app.config["IMAGE_STORE"],"").replace(self.filename,"")
                self.ensure_dir(webimages_path)

                fn, ext = os.path.splitext(self.filename)

                self.thumbPath = "%s%s_tm%s" % (webimages_path, fn, ext)
                self.mediumPath = "%s%s_md%s" % (webimages_path, fn, ext)
                self.largePath = "%s%s_lg%s" % (webimages_path, fn, ext)

                self.generate_webimages()
                self.size = os.path.getsize(imageSource)
        except Exception as e:
            print(e.args[0])

        self.persist()

    def ensure_dir(self,dirname):
        """
        Ensure that a named directory exists; if it does not, attempt to create it.
        """
        try:
            os.makedirs(dirname)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

    def imageFromDB(self, imageSource):
        blacklist = [ "exif"]
        for field in imageSource:
            if not field in blacklist:
                if field == "_id":
                    setattr(self,"id",imageSource[field])
                else:
                    setattr(self,field,imageSource[field])

    def persist(self):
        imgobject = {}
        blacklist = ["id", "exif"]
        for field in self.__dict__:#ImagePersistedFields:
            if not field in blacklist:
                imgobject[field] = getattr(self,field)
        im_id = imagesDB.update({"dateTaken":self.dateTaken}, {"$set":imgobject}, upsert=True)
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
            return None

    def __str__(self):
        return self.path

    def generate_webimages(self):

        im = Image.open(self.originalPath)

        size = 800, 640

        if not os.path.isfile(self.mediumPath):

            im.thumbnail(size, Image.ANTIALIAS)
            im.save(self.mediumPath, "JPEG")

        size = (256, 256)

        if not os.path.isfile(self.thumbPath):

            thumb = ImageOps.fit(im, size, Image.ANTIALIAS)
            thumb.save(self.thumbPath, "JPEG")
