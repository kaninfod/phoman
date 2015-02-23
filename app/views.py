from flask import render_template


from app import app, model
from app.model import *
from app.model.imageCollection import imageCollection




@app.route('/')
def artists():
    common.indexImages("/home/martin/Pictures/000 Master - Auto Backup/2014/12")

    cl = imageCollection({'make':'LGE'})

    #k = common.populateCollection(cl)
    common.findImages()
    data = "hello world"
    return render_template('home.html', data=data)
