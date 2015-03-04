from flask import render_template


from app import app
from app import collectionsDB
from app.model import *
from app.model.imageCollection import imageCollection
import datetime
from .forms import newCollectionForm
from flask import request, flash, redirect, url_for



@app.route('/sync')
def sync():
    common.indexImages("/home/martin/Pictures/000 Master - Auto Backup/2014")


    return render_template('home.html', data=data)



@app.route('/images',  defaults={'page':1})
@app.route('/images/page/<int:page>')
def images(page):

    perPage = 10
    data = col = imageCollection("54f3d981ec4a5caab5af6037")
    pagination = common.pagination(page, perPage, data.imagecount)
    data = data[pagination.min_rec:pagination.max_rec]
    common.getCollections()


    return render_template('images.html', data=data, paginator=pagination)


@app.route('/collections',  defaults={'page':1})
@app.route('/collections/page/<int:page>')
def collection(page):

    perPage = 4
    data = collectionsDB.find()
    pagination = common.pagination(page, perPage, data.count())
    data = data[pagination.min_rec:pagination.max_rec]



    return render_template('collections.html', data=data, paginator=pagination)

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


def url_for_other_page(page):
    args = request.view_args.copy()
    args['page'] = page
    return url_for(request.endpoint, **args)
app.jinja_env.globals['url_for_other_page'] = url_for_other_page