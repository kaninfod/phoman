__author__ = 'martin'

from photo_tank.model.database import Database
from photo_tank.model.photo import Photo


class Album():
    def __init__(self, album_id=None):
        self.tags_include = []
        self.tags_exclude = []
        self.selected = []
        self.startdate = None
        self.enddate = None
        self.selected_only = None
        self.name = ""
        self.type = {}
        self.id = album_id
        self.image_count = ""
        self.image_collection = []
        self._paginator = None
        self._position = 0
        self.db = Database()

        if album_id:
            self._get_collection()


    @property
    def paginator(self):
        return self._paginator

    @paginator.setter
    def paginator(self, paginator):
        self._position = paginator.min_rec
        self._paginator = paginator


    def __iter__(self):
        return self

    def __next__(self):

        if self.image_collection:
            self._position += 1
            if self._paginator:
                if self._position - 1 < self.paginator.max_rec:
                    return Photo(image_id=self.image_collection[self._position-1])
                else:
                    raise StopIteration()
            else:
                if self._position <= len(self.image_collection):
                    return Photo(image_id=self.image_collection[self._position-1])
                else:
                    raise StopIteration()

        else:

            raise StopIteration()

    def __getitem__(self, index):

        if isinstance(index, int):
            return Photo(self.image_collection[index])
        elif isinstance(index, slice):
            return self.image_collection[index.start:index.stop]

    def _get_collection(self):
        if self.id:
            record = self.db.get_album(self.id)
            if record:
                self.id = record["_id"]
                self.name = record["name"]
                self.tags_exclude = record["tags_exclude"]
                self.tags_include = record["tags_include"]
                self.startdate = record["startdate"]
                self.enddate = record["enddate"]
                self.selected_only = record["selected_only"]
                self.selected = record["selected"]
                self.type = record["type"]
                self._get_images()

    def _get_images(self):
        self.image_collection = self.db.get_images_in_album(self)


    def save(self):
        self.db.save_album(self)
        self._get_images()
