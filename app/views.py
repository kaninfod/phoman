from flask import render_template

import app.model
from app import app, model
from app.model import image


@app.route('/')
def artists():
    image.indexImages()
    model.images.test()
    data = "hello world"
    return render_template('home.html', data=data)
