from flask.ext.wtf import Form
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired


class newCollectionForm(Form):
    collectionName = StringField('Collection Name')
    make = StringField('Make')
    model = StringField('Model')