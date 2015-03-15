from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, DateField, validators, SelectMultipleField, HiddenField, SubmitField
from app.model.common import get_keywords


class newCollectionForm(Form):
    collectionName = StringField('Collection Name', [validators.InputRequired()])

    make = StringField('Make')
    model = StringField('Model')
    dateTaken_gt = DateField("Taken on or after", [validators.optional()])
    dateTaken_lt = DateField("Taken before", [validators.optional()])


class new_album(Form):
    id = HiddenField()
    name = StringField('Album name', [validators.InputRequired()])
    tags_include = SelectMultipleField('Tags included', choices=get_keywords())
    tags_exclude = SelectMultipleField('Tags Excluded', choices=get_keywords())
    submit = SubmitField("Save")