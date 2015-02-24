__author__ = 'martin'

from app.model.image import image
from app import db
from math import ceil


class imageCollection():

    def __init__(self, query):

        self.image_db = db['images']
        self.query = query
        self.cursor = self.image_db.find(self.query)
        print()

    def __iter__(self):
        return self

    def __next__(self):

        if self.cursor and self.cursor.alive:
            return image(next(self.cursor))
        else:
            raise StopIteration()

    def __getitem__(self, i):
        if isinstance(i, int):
            return image(self.cursor[i])
        elif isinstance(i,slice):
            l = list()
            self.cursor.rewind()
            for j in self.cursor[i.start:i.stop]:
                 l.append(image(j))
            return l

class paginateor():
    def __init__(self, perPage, totalCount, page):
        self.perPage = perPage
        self.totalCount = totalCount
        self.page = page


    def pages(self):
        return int(ceil(self.totalCount / float(self.perPage)))

    def has_prev(self):
        return self.page > 1

    def has_next(self):
        return self.page < self.pages


    def iterPages(self):
        for num in range(1, self.pages + 1):
            yield num
