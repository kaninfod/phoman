from flask import render_template


from app import app
from app import collectionsDB
from app.model import *
from app.model.imageCollection import imageCollection
import datetime
import calendar
from .forms import newCollectionForm
from flask import request, flash, redirect, url_for, send_from_directory, send_file, safe_join



@app.route('/sync')
def sync():
    common.indexImages()


    return render_template('home.html')


@app.route('/imagestore')
def imagestore():
    relative_path = request.args["path"]

    return send_file(relative_path)

@app.route('/showlarge')
def showlarge():
    data = request.args["path"]

    return render_template('showlarge.html', data=data)


@app.route('/images/id/<id>',  defaults={'page':1})
@app.route('/images/id/<id>/page/<int:page>')
def images(id, page):

    perPage = 25
    data = imageCollection(id)
    pagination = common.pagination(page, perPage, data.imagecount)
    data = data[pagination.min_rec:pagination.max_rec]



    return render_template('images.html', data=data, paginator=pagination)


@app.route('/collections',  defaults={'page':1})
@app.route('/collections/page/<int:page>')
def collection(page):

    perPage = 9
    data = collectionsDB.find()
    pagination = common.pagination(page, perPage, data.count())
    data = data[pagination.min_rec:pagination.max_rec]



    return render_template('collections.html', data=data, paginator=pagination)

@app.route('/addcollection',  methods=['GET', 'POST'])
def addCollection():

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


@app.route('/updateimagecounts')
def updateimagecounts():
    common.getCollections()
    return redirect('/collections')


@app.route('/')
def home():

    return render_template('home.html')


@app.route('/addCol')
def addCol():
    for i in range(1,12):
        col = imageCollection()
        col.name = "2014-%s" % i

        col.query.dateTaken_gt = datetime.date(2014, i, 1)
        m = calendar.monthrange(2014,i)
        col.query.dateTaken_lt = datetime.date(2014, i, m[1])
        col.save()

    return redirect('/collections')

def url_for_other_page(page):
    args = request.view_args.copy()
    args['page'] = page
    return url_for(request.endpoint, **args)
app.jinja_env.globals['url_for_other_page'] = url_for_other_page