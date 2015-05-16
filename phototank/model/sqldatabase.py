__author__ = 'hingem'

from peewee import *
from phototank.app import sqldb
import datetime















def save_me(photo):

    try:
        #DBPhoto.create_table()
        #Location.create_table()
        #Keyword.create_table()
        record = DBPhoto.get(image_hash=photo.image_hash)
        pass
    except DBPhoto.DoesNotExist as e:
        dbp = DBPhoto()
        try:
            dbp.date_taken=photo.date_taken
            dbp.make=photo.make
            dbp.model=photo.model
            dbp.ImageUniqueID=photo.ImageUniqueID
            dbp.has_exif=photo.has_exif
            dbp.modified=photo.modified
            dbp.original_height=photo.original_height
            dbp.original_width=photo.original_width
            dbp.orientation=photo.orientation
            dbp.flash_fired=photo.flash_fired
            dbp.image_hash=photo.image_hash
            dbp.file_name = photo.files.filename
            dbp.file_original_subpath = photo.files.original_subpath
            dbp.file_extension = photo.files.extension
            dbp.file_original_path = photo.files.original_path
            dbp.file_large_path = photo.files.large_path
            dbp.file_medium_path = photo.files.medium_path
            dbp.file_thumb_path = photo.files.thumb_path
            dbp.file_size = photo.files.size
            #dbp.dropbox_modified=photo.dropbox.modified
            #dbp.dropbox_revision=photo.dropbox.revision
            #dbp.dropbox_size=photo.dropbox.size
            #dbp.dropbox_path=photo.dropbox.path

            loc = DBLocation.create(address=photo.location.address)
            dbp.location = loc
            loc.status = photo.location.status
            loc.latitude = photo.location.latitude
            loc.longitude = photo.location.longitude
            loc.location = photo.location.location
            loc.country = photo.location.country
            loc.state = photo.location.state
            loc.address = photo.location.address
            loc.road = photo.location.road
            loc.city = photo.location.city
            loc.suburb = photo.location.suburb
            loc.postcode = photo.location.postcode

            kw = DBKeyword()
            kw.category = "File"
            kw.subcategory = 'Size'
            kw.sortorder = '5'
            kw.value = "test"
            kw.save()
            dbp.save()
            m = DBPhotoKeyword.create(keyword=kw, photo=dbp)

            pass


        except Exception as e:
            print(e)

