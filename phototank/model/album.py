__author__ = 'martin'
from peewee import *
from phototank.app import db
from phototank.model.photo import Photo, Keyword, PhotoKeyword
class Album(db.Model):

    selected = TextField(null=True)
    startdate = DateTimeField(null=True)
    enddate = DateTimeField(null=True)
    selected_only = BooleanField(null=True)
    name = TextField(null=True)
    photo_count = IntegerField(null=True, default=0)
    #type = {}


    _image_collection = None
    _paginator = None
    _position = 0
    _photo_count = 0


    def __iter__(self):
        return self

    def __next__(self):

        if self._image_collection:
            return next(self._image_collection)

    def __getitem__(self, index):

        if isinstance(index, int):
            return Photo(self.image_collection[index])
        elif isinstance(index, slice):
            return self.image_collection[index.start:index.stop]

    def get_photos(self):
        pc = Photo.select().join(PhotoKeyword, on=PhotoKeyword.photo).where(PhotoKeyword.keyword==6)
        self._photo_count = pc.count()
        return pc

    @property
    def photo_count(self):
         #self._photo_count = Photo.select().count()
         return self._photo_count

    @property
    def paginator(self):
        return self._paginator

    @paginator.setter
    def paginator(self, paginator):
        self._image_collection = self.get_photos().paginate(paginator.page, paginator.per_page)
        self._image_collection = iter(self._image_collection)

    def add_keyword(self, keyword, type):
        try:
            exists = AlbumKeyword.select(AlbumKeyword.album==self, AlbumKeyword.keyword==keyword, AlbumKeyword.type==type)
        except AlbumKeyword.DoesNotExist:
            m = AlbumKeyword.create(album=self, keyword=keyword, type=type)

    def keywords_include(self):
        kw = Keyword  \
            .select() \
            .join(AlbumKeyword, on=AlbumKeyword.keyword)\
            .where(AlbumKeyword.album==self, AlbumKeyword.type==1)
        lkw = [k for k in kw]
        return lkw

    def keywords_exclude(self):
        kw = Keyword  \
            .select() \
            .join(AlbumKeyword, on=AlbumKeyword.keyword)\
            .where(AlbumKeyword.album==self, AlbumKeyword.type==2)
        lkw = [k for k in kw]
        return lkw

class AlbumKeyword(db.Model):
    album = ForeignKeyField(Album)
    keyword = ForeignKeyField(Keyword)
    type = IntegerField(null=True)


for table in [Album, AlbumKeyword]:
    try:
        table.create_table()
    except Exception as e:
        print(e)






#from phototank.model.database import Database
#from phototank.model.photo import Photo


# class Album():
#     def __init__(self, album_id=None):
#         self.tags_include = []
#         self.tags_exclude = []
#         self.selected = []
#         self.startdate = None
#         self.enddate = None
#         self.selected_only = None
#         self.name = ""
#         self.type = {}
#         self.id = album_id
#         self._photo_count = ""
#         self.image_collection = None
#         self._paginator = None
#         self._position = 0
#         self.db = Database()
#
#         if album_id:
#             self._get_collection()
#
#     @property
#     def photo_count(self):
#         self._photo_count = self.db.photo_count(self)
#         return self._photo_count
#
#
#     @property
#     def paginator(self):
#         return self._paginator
#
#     @paginator.setter
#     def paginator(self, paginator):
#         self._position = paginator.min_rec
#         self._paginator = paginator
#
#
#     def __iter__(self):
#         return self
#
#     def __next__(self):
#
#         if self.image_collection:
#             self._position += 1
#             if self._paginator:
#                 if self._position <= self.paginator.max_rec:
#                     r = next(self.image_collection)
#                     p = Photo(r)
#                     return p
#                 else:
#                     raise StopIteration()
#             else:
#                 if self._position <= self.image_collection.count():
#                     return Photo(image_id=next(self.image_collection))
#                 else:
#                     raise StopIteration()
#
#         else:
#
#             raise StopIteration()
#
#     def __getitem__(self, index):
#
#         if isinstance(index, int):
#             return Photo(self.image_collection[index])
#         elif isinstance(index, slice):
#             return self.image_collection[index.start:index.stop]
#
#     def _get_collection(self):
#         if self.id:
#             record = self.db.get_album(self.id)
#             if record:
#                 self.id = record["_id"]
#                 self.name = record["name"]
#                 self.tags_exclude = record["tags_exclude"]
#                 self.tags_include = record["tags_include"]
#                 self.startdate = record["startdate"]
#                 self.enddate = record["enddate"]
#                 self.selected_only = record["selected_only"]
#                 self.selected = record["selected"]
#                 self.type = record["type"]
#                 #self._get_images()
#
#     def _get_images(self):
#         self.image_collection = self.db.get_photos_in_album(self)
#
#     def get_images(self):
#         self.image_collection = self.db.get_photos_in_album(self, skip=self.paginator.min_rec, limit=self.paginator.per_page)
#
#     def save(self):
#         self.db.save_album(self)
#         self._get_images()
