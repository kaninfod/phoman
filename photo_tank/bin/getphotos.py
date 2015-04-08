__author__ = 'hingem'



import os
import sys
from PIL import Image

from datetime import datetime

from PIL import ExifTags
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
            print("could not do " + source_full_file_path)


def main():
    source = "/Users/hingem/my_image_store"
    destination = "/Users/hingem/my_image"
    doNaming(source, destination)



if __name__ == '__main__':
    main()
