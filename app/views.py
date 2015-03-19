from flask import render_template

from app import app
from app import collectionsDB
from app import albumsDB
import os
from app.model import *
from app.model.imageCollection import imageCollection
from app.model.common import get_keywords

from app.model.album import Album
from app.model.image import image, ImageQuery
import datetime
import calendar
from .forms import newCollectionForm, new_album
from flask import request, flash, redirect, url_for, send_file, jsonify

@app.route('/')
@app.route('/home')
def home():

    return render_template('home.html')

@app.route('/image/store/image/<image_id>/size/<size>')
def imagestore(image_id, size):
    im = image(image_id=image_id)
    if im:
        if size == "tm":
            path = im.db_thumb_path
        elif size == "md":
            path = im.db_medium_path
        elif size == "lg":
            path = im.db_large_path

    return send_file(path)


@app.route('/image/large/id/<id>')
def showlarge(id):
    im = image(image_id=id)
    return render_template('showlarge.html', back_url=request.referrer, img=im)


#@app.route('/image/album/new', defaults={'album_id':5, 'page': 1})
@app.route('/image/album/<album_id>', defaults={'page': 1}, methods=['GET', 'POST'])
@app.route('/image/album/<album_id>/page/<int:page>')
def images(album_id, page):


    alb = Album(album_id)
    perPage = 12
    pagination = common.pagination(page, perPage, alb.imagecount)
    alb.paginator = pagination

    return render_template('images.html',
                           data=data,
                           paginator=pagination,
                           ajax=ajax,
                           album = alb,
                           keywords=get_keywords())



@app.route('/album/save/<album_id>', methods=['GET', 'POST'])
def album_save(album_id):
    ajax = False
    alb = Album(album_id)

    form_data = request.get_json()
    if form_data:
        alb.tags_include = form_data['included']
        alb.tags_exclude = form_data['excluded']
        alb.save()
    return jsonify({'status':'ok'})



@app.route('/album/list', defaults={'page': 1})
@app.route('/album/list/page/<int:page>')
def collection(page):
    perPage = 10
    data = albumsDB.find()
    pagination = common.pagination(page, perPage, data.count())
    data = data[pagination.min_rec:pagination.max_rec]

    return render_template('album_list.html', data=data, paginator=pagination)






@app.route('/addcollection/id/<id>', methods=['GET', 'POST'])
def addCollection():
    form = newCollectionForm()
    if request.method == "POST" and form.validate():
        col = imageCollection()
        col.query.db_make = form.make.data
        col.query.db_model = form.model.data
        col.name = form.collectionName.data
        col.query.date_taken_gte = form.dateTaken_gt.data
        col.query.date_taken_lt = form.dateTaken_lt.data
        col._save()
        flash(col.imagecount)
        return redirect('/addcollection')
    return render_template('addCollection.html', title="Add new collection", form=form)


@app.route('/sync')
def sync():
    alb = Album()
    alb.name = "my album"
    alb.tags_include = ["LGE"]
    alb.tags_exclude = ["Sunday"]
    alb._get_images()
    alb.save()

    return render_template('home.html')


def url_for_other_page(page):
    args = request.view_args.copy()
    args['page'] = page
    return url_for(request.endpoint, **args)


app.jinja_env.globals['url_for_other_page'] = url_for_other_page


