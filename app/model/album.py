__author__ = 'martin'


from app.model.image import image
from app.model.mongo_db import save_album, get_album, get_images_in_album

class Album():
    def __init__(self, album_id=None):
        self.tags_include = []
        self.tags_exclude = []
        self.name = ""
        self.id = album_id
        self.image_count = ""

        self.image_collection = []
        self._paginator = None
        self._position = 0

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

                    return image(image_id=self.image_collection[self._position-1])
                else:
                    raise StopIteration()
            else:
                return image(next(self.image_collection))

        else:

            raise StopIteration()

    def __getitem__(self, index):

        if isinstance(index, int):
            return image(self.image_collection[index])
        elif isinstance(index, slice):
            return self.image_collection[index.start:index.stop]

    def _get_collection(self):
        if self.id:
            record = get_album(self.id)
            if record:
                self.id = record["_id"]
                self.name = record["name"]
                self.tags_exclude = record["tags_exclude"]
                self.tags_include = record["tags_include"]

                self._get_images()

    def _get_images(self):
        self.image_collection = get_images_in_album(self)

    def save(self):
        save_album(self)
        self._get_images()
