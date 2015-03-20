from flask import render_template

from app import app
from app import albumsDB

from app.model import *
from app.model.common import get_keywords

from app.model.album import Album
from app.model.image import image
from flask import request,  url_for, send_file, jsonify

@app.route('/')
@app.route('/home')
def home():

    return render_template('home.html')

@app.route('/image/store/image/<image_id>/size/<size>')
def imagestore(image_id, size):
    im = image(image_id=image_id)
    if im:
        if size == "thumb":
            path = im.db_thumb_path
        elif size == "medium":
            path = im.db_medium_path
        elif size == "large":
            path = im.db_large_path
        elif size == "original":
            path = im.db_original_path
    return send_file(path)


@app.route('/image/<size>/<id>')
def showlarge(size, id):
    im = image(image_id=id)
    return render_template('showlarge.html', back_url=request.referrer, size=size, img=im)



@app.route('/image/album/<album_id>', defaults={'page': 1}, methods=['GET', 'POST'])
@app.route('/image/album/<album_id>/page/<int:page>')
def images(album_id, page):


    alb = Album(album_id)
    perPage = 20
    pagination = common.pagination(page, perPage, alb.imagecount)
    alb.paginator = pagination

    return render_template('images.html',paginator=pagination,album = alb, keywords=get_keywords())



@app.route('/album/save/<album_id>', methods=['GET', 'POST'])
def album_save(album_id):

    alb = Album(album_id)

    form_data = request.get_json()
    if form_data:
        alb.name = form_data['name']
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



def url_for_other_page(page):
    args = request.view_args.copy()
    args['page'] = page
    return url_for(request.endpoint, **args)


app.jinja_env.globals['url_for_other_page'] = url_for_other_page


