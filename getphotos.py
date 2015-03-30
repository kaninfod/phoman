__author__ = 'hingem'


import logging
import gdata.photos.service
import gdata.media
import gdata.geo
import urllib2
import os
import sys
import exifread
from datetime import datetime
import Image
from PIL import ExifTags   # This is provided by PIL



logging.basicConfig(format='%(asctime)s %(message)s',filename='goog.log',level=logging.WARNING)

BASEPATH = "/home/martin/Pictures"
EMAIL = "martinhinge@gmail.com"
PASSWORD = "Lizzard7"

class google:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.client = self.login(email=email, password=password)
        self.albums = self.getAlbums()


    def login(self, email, password):
        gd_client = gdata.photos.service.PhotosService()
        gd_client.email = email
        gd_client.password = password
        gd_client.source = 'exampleCo-exampleApp-1'
        gd_client.ProgrammaticLogin()
        return gd_client


    def getAlbums(self):
        return self.client.GetUserFeed(user=self.email)


    def getAlbumById(self, id):
        for album in self.albums.entry:
            if album.gphoto_id.text == id:
                return album



    def getPhotos(self, album, num, begin):
        return self.client.GetFeed('/data/feed/api/user/%s/albumid/%s?kind=photo&imgmax=d&max-results=%s&start-index=%s' % (self.email, album.gphoto_id.text,num,begin))


    def saveAlbum(self, album):
        n=1
        NumPhotosToRead = 500
        while True:

            photos = self.getPhotos(album, NumPhotosToRead, n)
            n += NumPhotosToRead

            logging.warning("Downloading album: '%s', id: '%s',  number of photos: %s", album.title.text,
                            album.gphoto_id.text, album.numphotos.text)

            localDir = album.title.text.replace("/","_")
            localDir = BASEPATH + "/" + localDir

            if not os.path.exists(localDir):
                os.mkdir(localDir)
                logging.info("Directory created: '%s", localDir)



            photosInAlbum ={}

            for photo in photos.entry:

                remote = photo.media.content[0].url
                mime = photo.media.content[0].type
                if mime == 'image/jpeg':
                    extension = "jpg"
                elif mime == 'image/gif':
                    extension = "gif"
                elif mime == 'image /gif':
                    extension = "mp4"
                else:
                    extension = "unknown"



                basename = photo.gphoto_id.text + "." + extension

                local = localDir + "/" + basename

                photosInAlbum[photo.gphoto_id.text] = {
                    'local': local,
                    'localDir': localDir,
                    'extension': extension,
                    'remote': remote,
                    'remoteSize':int(photo.size.text)
                }


                self.downloadfile(remote, local)

            logging.warning("Number of processed photos: '%s',  number of photos in album: %s",len(photosInAlbum),
                            album.numphotos.text)

            if len(photos.entry) < NumPhotosToRead: break
            #for photo in photosInAlbum.itervalues():
            #    if os.path.getsize(photo['local']) == photo['remoteSize']:
            #        logging.warning("Filesizes match for: '%s'", photo['local'])
            #    try:
            #       self.changeName(photo)
            #    except:
            #        print




    def downloadfile(self, remote, local):

        u = urllib2.urlopen(remote)
        h = u.info()
        totalSize = int(h["Content-Length"])
        if os.path.isfile(local):
            if os.path.getsize(local) == totalSize:
                logging.warning("File with same size exist - no action: '%s' - size: %s", local, totalSize)
                return 1
            else:
                logging.warning("File exists but size different - overwriting: '%s'", local)

        fp = open(local, 'wb')

        blockSize = 8192
        count = 0
        while True:
            chunk = u.read(blockSize)
            if not chunk: break
            fp.write(chunk)
            count += 1


        fp.flush()
        fp.close()
        #logging.warning("File downloaded: '%s', size: %s", local, os.path.getsize(local))
        return 2


        if not totalSize:
            print

    def changeName(self, photo):

        f = open(photo['local'], 'rb')
        tags = exifread.process_file(f)
        photoDate = tags['EXIF DateTimeOriginal'].printable
        filename = datetime.strptime(photoDate, "%Y:%m:%d %H:%M:%S").strftime('%m%d%Y_%H%M%S')
        os.rename(photo['local'], photo['localDir'] + "/" + filename + "." + photo['extension'])




def printAlbums(google):
    for alb in google.albums.entry:
        print alb.gphoto_id.text, alb.numphotos.text, alb.title.text


def listDirs(dir):



    for subdir, dirs, files in os.walk(dir):
        for file in files:
            yield (subdir, file)  #os.path.join
    return


def doNaming(source, destination):
    import glob
    import os
    import shutil





    for file in listDirs(source):
        source_file_path, source_file_name = file
        source_full_file_path = os.path.join(source_file_path,source_file_name)
        s,file_ext = os.path.splitext(source_file_name)
        source_file_size = os.path.getsize(source_full_file_path)


        try:

            img=Image.open(source_full_file_path,'r')

            exif = {
                ExifTags.TAGS[k]: v
                for k, v in img._getexif().items()
                if k in ExifTags.TAGS
            }



            photoDate = str(exif["DateTimeOriginal"])
            photoDate = datetime.strptime(photoDate, "%Y:%m:%d %H:%M:%S")
            photo_year = photoDate.strftime("%Y")
            photo_month = photoDate.strftime("%m")
            photo_day = photoDate.strftime("%d")
            photo_hour = photoDate.strftime("%H")
            photo_minute = photoDate.strftime("%M")
            photo_second = photoDate.strftime("%S")

            destination_file_name = "%s%s%s_%s%s%s%s" % (photo_year, photo_month, photo_day,photo_hour, photo_minute,photo_second, file_ext)
            destination_file_name = destination_file_name.lower()
            new_file_path = os.path.join(destination, photo_year, photo_month,photo_day)
            destination_full_file_path = os.path.join(new_file_path,destination_file_name)



            if not os.path.exists(os.path.join(new_file_path,destination_file_name)):
                new_dir = destination + "/" + photo_year
                if not os.path.exists(new_dir):
                        os.mkdir(new_dir)

                new_dir = new_dir + "/" + photo_month
                if not os.path.exists(new_dir):
                        os.mkdir(new_dir)

                new_dir = new_dir + "/" + photo_day
                if not os.path.exists(new_dir):
                        os.mkdir(new_dir)


            if os.path.exists(destination_full_file_path):
                new_file_size = os.path.getsize(destination_full_file_path)
            else:
                new_file_size = source_file_size

            if not source_full_file_path == destination_full_file_path:
                if source_file_size == new_file_size:
                    shutil.move(source_full_file_path, destination_full_file_path)
                print(source_full_file_path)
                if source_file_size > new_file_size:
                    min_file_path = os.path.join(new_file_path,"min_" + destination_file_name)
                    os.rename(destination_full_file_path, min_file_path)
                    os.rename(source_full_file_path, destination_full_file_path)
                elif source_file_size < new_file_size:
                    min_file_path = os.path.join(new_file_path,"min_" + destination_file_name)
                    os.rename(source_full_file_path,min_file_path)

        except  Exception as e:
            print "could not do " + source_full_file_path





def goog2date(path):

    for root, dirnames, filenames in os.walk(path):
        for filename in filenames:
            fn = root + "/" + filename
            try:

                img=Image.open(fn,'r')

                exif = {
                    ExifTags.TAGS[k]: v
                    for k, v in img._getexif().items()
                    if k in ExifTags.TAGS
                }



                photoDate = str(exif["DateTimeOriginal"])
                photoDate = datetime.strptime(photoDate, "%Y:%m:%d %H:%M:%S").strftime("%Y%m%d_%H%M%S")
                fileName, fileExtension = os.path.splitext(filename)
                if fileExtension == "":
                    fileExtension = ".jpg"

                os.rename(fn, root + "/" + photoDate  + fileExtension)
            except Exception as inst:
                print "could not do " + fn


def fixDirs(p):


    src = p

    for root, dirnames, filenames in os.walk(src):
        for dir in dirnames:
            if len(dir) == 1:
                os.rename(root + "/" + dir,root + "/" + "0" + dir)




def main():
    source = "/media/net/photos/2015/02"
    destination = "/media/net/photos"
    doNaming(source, destination)

    #goog2date(p)
    #p = "/media/net/photos/2014"
    #goog2date(p)
    exit()

    doNaming(p)
    fixDirs(p)

    k = google(EMAIL, PASSWORD)
    #printAlbums(k)
    with open('albums.cfg') as f:
        for line in f:
            a = k.getAlbumById(line.strip())
            k.saveAlbum(a)




if __name__ == '__main__':
    main()
