import os

from flask import request, url_for, send_file, jsonify, render_template, session, redirect
from phototank.app import app
from phototank.model.photo import Photo, Keyword
from phototank.model.album import Album, AlbumKeyword
from phototank.model.common import Pagination



import json
import time

#db = Database()


@app.route('/')
@app.route('/home')
def home():

    ph = Photo().select()

    return render_template('panel.html')

@app.route('/keywords')
def keywords():


    k = Keyword()
    term = (request.args.get('term'))
    li = k.json(query=term)

    r = json.dumps(li)
    return r

@app.route('/image/store/image/<image_id>/size/<size>')
def imagestore(image_id, size):
    photo = Photo.get(Photo.id==image_id)
    if photo:
        if size == "thumb":
            path = photo.file_thumb_path
        elif size == "medium":
            path = photo.file_medium_path
        elif size == "large":
            path = photo.file_large_path
        elif size == "original":
            path = photo.file_original_subpath
    return send_file(path)


@app.route('/image/<size>/<id>')
def showlarge(size, id):
    im = Photo.get(Photo.id==id)
    return render_template('showlarge.html', back_url=request.referrer, size=size, img=im)


@app.route('/image/album/new', defaults={'album_id': False, 'page': 1}, methods=['GET', 'POST'])
@app.route('/image/album/<album_id>', defaults={'page': 1}, methods=['GET', 'POST'])
@app.route('/image/album/<album_id>/page/<int:page>')
def images(album_id, page):
    cl = time.clock()
    if not album_id:
        album = Album()
        album.name = "__temp__"
        album.save()
        #if "temp_album" in session:
            #if session["temp_album"] != album.id:
                #album = Album.get(Album.name=='__temp__')
                #db.delete_album(session["temp_album"], {'name': '__temp__'})
        session["temp_album"] = album.id
        return redirect("/image/album/" + str(album.id))
    print(time.clock() - cl)
    album = Album.get(Album.id==album_id)
    keyword_array = album.keywords()

    print(time.clock() - cl)
    perPage = 27
    pagination = Pagination(page, perPage, album.photo_count)
    album.paginator = pagination

    print(time.clock() - cl)
    return render_template('image_viewer/images.html',
                           paginator=pagination,
                           album=album,
                           keywords=keyword_array
                           )


@app.route('/album/save/<album_id>', methods=['GET', 'POST'])
def album_save(album_id):
    album = Album.get(Album.id==album_id)

    form_data = request.get_json()
    if form_data:
        album.name = form_data['name']

        album.selected = form_data['selected']
        album.selected_only = form_data['selected_only']
        album.save()

        album.update_keywords(form_data['keywords'])


    return jsonify({'status': 'ok'})


@app.route('/album/list', defaults={'page': 1})
@app.route('/album/list/page/<int:page>')
def collection(page):
    perPage = 10
    data = Album.select()
    pagination = Pagination(page, perPage, data.count())


    return render_template('album_list.html', data=data, paginator=pagination)





def url_for_other_page(page):
    args = request.view_args.copy()
    args['page'] = page
    return url_for(request.endpoint, **args)


app.jinja_env.globals['url_for_other_page'] = url_for_other_page


