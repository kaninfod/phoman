from flask import render_template


from app import app
from app.model import *
from app.model.imageCollection import imageCollection
from datetime import datetime
from .forms import newCollectionForm
from flask import request



@app.route('/sync')
def artists():
    common.indexImages("/home/martin/Pictures/000 Master - Auto Backup/2014")


    return render_template('home.html', data=data)

@app.route('/addcollection',  methods=['GET', 'POST'])
def addCollection():
    col = imageCollection("54f13fba63813cec0f91f243")
    k = col[1]
    print(k)
    form = newCollectionForm()
    if request.method == "POST":
        col = imageCollection()
        col.query.make = form.make.data
        col.query.model = form.model.data
        col.name = form.collectionName.data
        col.save()

    return render_template('addCollection.html', title="Add new collection", form=form)


