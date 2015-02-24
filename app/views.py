from flask import render_template


from app import app, model
from app.model import *
from app.model.imageCollection import imageCollection
from datetime import datetime



@app.route('/')
def artists():
    #common.indexImages("/Users/hingem/Dropbox/Camera Uploads")

    cl = imageCollection({'make':'SAMSUNG'})



    data = cl[3:13]
    return render_template('home.html', data=data)
