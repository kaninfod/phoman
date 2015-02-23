from flask import render_template


from app import app, model
from app.model import *




@app.route('/')
def artists():
    common.indexImages("/Users/hingem/Dropbox/Camera Uploads")

    data = "hello world"
    return render_template('home.html', data=data)
