import os


from flask import request,  url_for, send_file, jsonify, render_template, session, redirect
from photo_tank.app import app
from photo_tank.model.album import Album
from photo_tank.model.photo import Photo
from photo_tank.model.database import Database
from photo_tank.model.common import Pagination
import time
db = Database()


@app.route('/')
@app.route('/home')
def home():

    return render_template('home.html')

@app.route('/image/store/image/<image_id>/size/<size>')
def imagestore(image_id, size):
    im = Photo(image_id=image_id)
    if im:
        if size == "thumb":
            path = im.files.thumb_path
        elif size == "medium":
            path = im.files.medium_path
        elif size == "large":
            path = im.large_path
        elif size == "original":
            path = im.files.original_subpath
    return send_file(path)


@app.route('/image/<size>/<id>')
def showlarge(size, id):
    im = Photo(image_id=id)
    return render_template('showlarge.html', back_url=request.referrer, size=size, img=im)


@app.route('/image/album/new', defaults={'album_id': False, 'page': 1}, methods=['GET', 'POST'])
@app.route('/image/album/<album_id>', defaults={'page': 1}, methods=['GET', 'POST'])
@app.route('/image/album/<album_id>/page/<int:page>')
def images(album_id, page):
    ts = time.clock()
    if not album_id:
        alb = Album()
        alb.name = "__temp__"
        alb.save()
        if "temp_album" in session:
            if session["temp_album"] != alb.id:
                db.delete_album(session["temp_album"], {'name':'__temp__'})
        session["temp_album"] = alb.id
        return redirect("/image/album/" + alb.id)
    else:
        alb = Album(album_id)
    app.logger.debug("set album {}".format((time.clock() - ts)*1000))
    perPage = 24
    pagination = Pagination(page, perPage, alb.image_count)
    alb.paginator = pagination
    alb.get_images()
    app.logger.debug("get images {}".format((time.clock() - ts)*1000))
    kw = db.get_keywords()
    app.logger.debug("get kw {}".format((time.clock() - ts)*1000))
    ct = db.get_keyword_categories()
    app.logger.debug("cats {}".format((time.clock() - ts)*1000))
    return render_template('image_viewer/images.html',
                           paginator=pagination,
                           album = alb,
                           keywords=kw,
                           categories=ct
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
    data = db.get_albums()
    pagination = Pagination(page, perPage, data.count())
    data = data[pagination.min_rec:pagination.max_rec]

    return render_template('album_list.html', data=data, paginator=pagination)

UPLOAD_FOLDER = '/tmp/'
ALLOWED_EXTENSIONS = set(['txt'])


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# def allowed_file(filename):
#     return '.' in filename and \
#            filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
#
# @app.route("/ups", methods=['GET', 'POST'])
# def index():
#     if request.method == 'POST':
#         file = request.files['file']
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#             return redirect(url_for('index'))
#     return """
#     <!doctype html>
#     <title>Upload new File</title>
#     <h1>Upload new File</h1>
#     <form action="" method=post enctype=multipart/form-data>
#       <p><input type=file name=file>
#          <input type=submit value=Upload>
#     </form>
#     <p>%s</p>
#     """ % "<br>".join(os.listdir(app.config['UPLOAD_FOLDER'],))


def url_for_other_page(page):
    args = request.view_args.copy()
    args['page'] = page
    return url_for(request.endpoint, **args)


app.jinja_env.globals['url_for_other_page'] = url_for_other_page


