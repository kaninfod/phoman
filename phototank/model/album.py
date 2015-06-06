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
    _photo_count = -1


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

        include = [kw["id"] for kw in self.keywords() if kw["action"]==1]
        exclude = [kw["id"] for kw in self.keywords() if kw["action"]==2]
        if len(include):
            photos_include = Photo.select().join(PhotoKeyword, on=PhotoKeyword.photo).where((PhotoKeyword.keyword.in_(include)))
        else:
            photos_include = Photo.select()
        photos_exclude = Photo.select().join(PhotoKeyword, on=PhotoKeyword.photo).where((PhotoKeyword.keyword.in_(exclude)))
        photos = (photos_include - photos_exclude).distinct().order_by(SQL('date_taken'))

        self.photo_count = photos.count()
        return photos

    @property
    def photo_count(self):
        if self._photo_count == -1:
            self.get_photos()


        return self._photo_count

    @photo_count.setter
    def photo_count(self, value):
        self._photo_count = value


    @property
    def paginator(self):
        return self._paginator

    @paginator.setter
    def paginator(self, paginator):
        self._image_collection = self.get_photos().paginate(paginator.page, paginator.per_page)
        self._image_collection = iter(self._image_collection)

    def update_keywords(self, keywords):
        self.remove_keywords()
        for keyword in keywords:
            self.add_keyword(keyword["id"], keyword["action"])

    def remove_keywords(self):
        rec = AlbumKeyword.delete().where(AlbumKeyword.album == self)
        k = rec.execute()


    def add_keyword(self, keyword_id, type):

        exists = AlbumKeyword.select().where((AlbumKeyword.album==self) & (AlbumKeyword.keyword==keyword_id) & (AlbumKeyword.type==type))
        if not exists.count():
            m = AlbumKeyword.create(album=self, keyword=keyword_id, type=type)


    def keywords(self):
        # include is type 1
        # exclude is type 2
        keyword_array = []
        for k in self.keywords_include():
            keyword_array.append(
                {'category':k.category, 'subcategory':k.subcategory, 'value':k.value, 'id':str(k.id), 'action':1}
            )
        for k in self.keywords_exclude():
            keyword_array.append(
                {'category':k.category, 'subcategory':k.subcategory, 'value':k.value, 'id':str(k.id), 'action':2}
            )
        return keyword_array

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


