__author__ = 'hingem'


import os
import app
from app.model.mongo_db import *
import unittest
import tempfile

class FlaskrTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING']=True
        app.config['DB_NAME'] = 'test_db'


    def tearDown(self):
        pass



if __name__=='__main__':

    unittest.main()
