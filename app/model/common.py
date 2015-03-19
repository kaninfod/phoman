__author__ = 'martin'

import os
from app import *

from app.model.imageCollection import imageCollection, image
from app import collectionsDB, albumsDB
from math import ceil


def do_loop(loop):
    path = app.config["IMAGE_STORE"]
    for root, dirnames, filenames in os.walk(path):
        for filename in filenames:
            if os.path.splitext(filename)[1] == ".jpg":
                fn = root + "/" + filename
                img = image(fn)
                print(filename)
    loop.stop()





def get_collections():
    col_db = collectionsDB.find()
    for c in col_db:
        col = imageCollection(c['_id'])

    return collectionsDB.find()


def get_keywords():
    keywords = imagesDB.distinct('db_tags')
    k = [([x, y]) for x, y in zip(keywords, keywords)]

    return k


class pagination(object):
    def __init__(self, page, per_page, total_count):
        self.page = page
        self.per_page = per_page
        self.total_count = total_count

    @property
    def min_rec(self):
        return (self.page - 1) * self.per_page


    @property
    def max_rec(self):
        return min(self.page * self.per_page, self.total_count)


    @property
    def pages(self):
        return int(ceil(self.total_count / float(self.per_page)))

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.pages

    def iter_pages(self, left_edge=1, left_current=2,
                   right_current=4, right_edge=1):
        last = 0
        for num in range(1, self.pages + 1):
            if num <= left_edge or (
                                    self.page - left_current - 1 < num < self.page + right_current) or num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num


