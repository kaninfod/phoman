import os
from app import db
from app import cache

class image(db.Document):
    id = db.UUIDField()
    OriginalDate = db.StringField(required=False, unique=True)


def indexImages():
    img = image()
    img.OriginalDate = 'xyz'
    img.save()