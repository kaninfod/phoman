from app import app

from app.model.mongo_db import get_image_from_id, save_image, get_albums, get_keywords, delete_album, get_keyword_categories
from app.model import *

from app.model.album import Album
from app.model.image import image
from flask import request,  url_for, send_file, jsonify, render_template, g, session

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
            path = im.db_original_subpath
    return send_file(path)


@app.route('/image/<size>/<id>')
def showlarge(size, id):
    im = image(image_id=id)
    return render_template('showlarge.html', back_url=request.referrer, size=size, img=im)


@app.route('/image/album/new', defaults={'album_id': False, 'page': 1}, methods=['GET', 'POST'])
@app.route('/image/album/<album_id>', defaults={'page': 1}, methods=['GET', 'POST'])
@app.route('/image/album/<album_id>/page/<int:page>')
def images(album_id, page):

    if not album_id:
        alb = Album()
        alb.name = "__temp__"
        alb.save()
        if "temp_album" in session:
            if session["temp_album"] != alb.id:
                delete_album(session["temp_album"], {'name':'__temp__'})
        session["temp_album"] = alb.id

    else:
        alb = Album(album_id)
    perPage = 24
    pagination = common.pagination(page, perPage, alb.image_count)
    alb.paginator = pagination

    return render_template('image_viewer/images.html',
                           paginator=pagination,
                           album = alb,
                           keywords=get_keywords(),
                           categories=get_keyword_categories()
                           )

@app.route('/album/save/<album_id>', methods=['GET', 'POST'])
def album_save(album_id):

    album = Album(album_id)

    form_data = request.get_json()
    if form_data:
        album.name = form_data['name']
        album.tags_include = form_data['included']
        album.tags_exclude = form_data['excluded']
        album.selected = form_data['selected']
        album.selected_only = form_data['selected_only']
        album.save()
    return jsonify({'status':'ok'})

@app.route('/album/list', defaults={'page': 1})
@app.route('/album/list/page/<int:page>')
def collection(page):
    perPage = 10
    data = get_albums()
    pagination = common.pagination(page, perPage, data.count())
    data = data[pagination.min_rec:pagination.max_rec]

    return render_template('album_list.html', data=data, paginator=pagination)



def url_for_other_page(page):
    args = request.view_args.copy()
    args['page'] = page
    return url_for(request.endpoint, **args)


app.jinja_env.globals['url_for_other_page'] = url_for_other_page


