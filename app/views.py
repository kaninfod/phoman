from flask import render_template


from app import app, model
from app.model import *
from app.model.imageCollection import imageCollection
from datetime import datetime



@app.route('/')
def artists():
    common.indexImages("/Users/hingem/Dropbox/Camera Uploads")
    cl = imageCollection(query={'make':'SAMSUNG'}, name="taken with samsung")
    start = datetime(2015, 1, 1)
    end = datetime(2011, 2, 1)
    cl = imageCollection(query={'dateTaken':{"$gte": start, "$lt": end}}, name="taken with samsung", saveToDB=True)
    album = imageCollection(query={'make':'SAMSUNG'}, name="taken with samsung", saveToDB=True)

    data = "cl"

    return render_template('home.html', data=data)

@app.route('/collections')
def listCollections():
    data = common.getCollections()[1:10]
    return render_template('home.html', data=data)
