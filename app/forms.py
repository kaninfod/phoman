from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, DateField, validators



class newCollectionForm(Form):
    collectionName = StringField('Collection Name',  [validators.InputRequired()])

    make = StringField('Make')
    model = StringField('Model')
    dateTaken_gt = DateField("Taken on or after", [validators.optional()])
    dateTaken_lt = DateField("Taken before", [validators.optional()])

