from flask import render_template


from app import app
from app.model import *
from app.model.imageCollection import imageCollection
import datetime
from .forms import newCollectionForm
from flask import request, flash, redirect, url_for



@app.route('/sync')
def artists():
    common.indexImages("/home/martin/Pictures/000 Master - Auto Backup/2014")


    return render_template('home.html', data=data)

@app.route('/addcollection',  methods=['GET', 'POST'])
def addCollection():
    col = imageCollection("54f2912708298c3a7af6b4d5")
    k = col[1]
    print(k)
    form = newCollectionForm(   )
    if request.method == "POST" and form.validate():
        col = imageCollection()
        col.query.make = form.make.data
        col.query.model = form.model.data
        col.name = form.collectionName.data
        col.query.dateTaken_gt = form.dateTaken_gt.data
        col.query.dateTaken_lt = form.dateTaken_lt.data
        col.save()
        flash(col.imagecount)
        return redirect('/addcollection')
    return render_template('addCollection.html', title="Add new collection", form=form)


