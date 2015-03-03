__author__ = 'martin'

import os
from app.model.image import image
from app.model.imageCollection import imageCollection
from app import collectionsDB
from math import ceil

def indexImages(path):

    for root, dirnames, filenames in os.walk(path):
        for filename in filenames:
            fn = root + "/" + filename
            img = image(fn)

def findImages():
    imgcol = imageCollection()
    print()


def getCollections():
    return collectionsDB.find()


class pagination(object):
    def __init__(self, page, per_page, total_count):
        self.page = page
        self.per_page = per_page
        self.total_count = total_count
        self.paging = self.getPaging()

    @property
    def pages(self):
        return int(ceil(self.total_count / float(self.per_page)))

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.pages

    def getPaging(self):
        p = []
        for i in self.iter_pages():
            p.append(i)
        return p


    def pagingObject(self):
        Obj = {}
        Obj["paging"] = self.getPaging()
        Obj["page"] = self.page
        Obj["pages"] = self.pages
        Obj["has_next"] = self.has_next
        Obj["has_prev"] = self.has_prev
        Obj["per_page"] = self.per_page

        return Obj



    def iter_pages(self, left_edge=2, left_current=2,
                   right_current=5, right_edge=2):
        last = 0
        for num in range(1, self.pages + 1):
            if num <= left_edge or (num > self.page - left_current - 1 and num < self.page + right_current) or num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num