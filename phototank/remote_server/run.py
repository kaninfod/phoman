__author__ = 'hingem'
from flask import Flask
from flask.ext import restful
import os

app = Flask(__name__)
api = restful.Api(app)
IMAGE_STORE = "/Users/hingem/image_server/"

class AddPhoto(restful.Resource):
    def get(self):
        return {'hello': 'world'}

    def post(self):
        if restful.request.method == 'POST':
            file = restful.request.files['file']
            filename = file.filename
            file.save(os.path.join(IMAGE_STORE, filename))

            return {"status":"file saved"}


        pass

api.add_resource(AddPhoto, '/')

if __name__ == '__main__':
    app.run(port=5001, debug=True)
