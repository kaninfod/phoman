from flask import render_template


from app import app, model
from app.model import *




@app.route('/')
def artists():
    common.indexImages("/home/martin/Pictures/000 Master - Auto Backup/2014/12")

    data = "hello world"
    return render_template('home.html', data=data)
