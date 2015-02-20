from app import app, models
from flask import render_template
from flask import request
from flask import url_for
import os



@app.route('/')
def artists():

    data = "hello world"
    return render_template('home.html', data=data)
