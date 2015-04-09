__author__ = 'hingem'
from flask import Flask
from flask.ext import restful

app = Flask(__name__)
api = restful.Api(app)

class AddPhoto(restful.Resource):
    def get(self):
        return {'hello': 'world'}

api.add_resource(AddPhoto, '/')

if __name__ == '__main__':
    app.run(port=5001, debug=True)
