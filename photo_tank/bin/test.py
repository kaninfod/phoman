__author__ = 'hingem'

#from photo_tank.app import app

#k=app.db
print("hello world")

import os
try:
    user_paths = os.environ['PYTHONPATH'].split(os.pathsep)
    print(user_paths)
except KeyError:
    print("no")
    user_paths = []