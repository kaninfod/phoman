__author__ = 'hingem'

from bin import indexer
import os
import shutil
from app import *
#from app.model.mongo_db import *
from app.model.database import Database
from app.model.image import image
from bin import indexer
import unittest
import tempfile

db = Database()



def init_paths():
    base_path = os.path.join(os.getcwd(), "files")
    app.config['TESTING']=True
    app.config['DB_NAME'] = 'test_db'

    app.config["IMAGE_STORE"] = os.path.join(base_path, "image_store")
    app.config["IMAGE_THUMBS"] = os.path.join(base_path, "thumbs")
    app.config["IMAGE_DETENTION"] = os.path.join(base_path, "detention")
    app.config["OTHER_FILES"] = os.path.join(base_path, "other")
    app.config["IMAGE_WATCH_FOLDER"] = os.path.join(base_path, "watch")
    db.reinitialize()

class TestIndexNewFile(unittest.TestCase):


    def setUp(self):
        init_paths()
        self.src_files = os.path.join(os.getcwd(), "test_files")

    def tearDown(self):
        db.drop_database(app.config['DB_NAME'])

        src_path = os.path.join(app.config["IMAGE_STORE"],"2014","11","22","20141122_154645.jpg")
        dst_path = os.path.join(self.src_files, "test_image_1.jpg")
        shutil.move(src_path, dst_path)

        base_path = os.path.join(os.getcwd(), "files")
        shutil.rmtree(base_path)

    def test_run(self):

        test_file_path = os.path.join(self.src_files, "test_image_1.jpg")
        result = indexer.index_jpeg_file(test_file_path)
        self.assertTrue(os.path.exists(result.original_path))
        self.assertTrue(os.path.exists(result.large_path))
        self.assertTrue(os.path.exists(result.thumb_path))
        self.assertTrue(os.path.exists(result.medium_path))


class TestIndexExistingFile(unittest.TestCase):

    def setUp(self):
        init_paths()
        self.src_files = os.path.join(os.getcwd(), "test_files")


    def tearDown(self):
        db.drop_database(app.config['DB_NAME'])

        src_path = os.path.join(app.config["IMAGE_STORE"],"2014","11","22","20141122_154645.jpg")
        dst_path = os.path.join(self.src_files, "test_image_1.jpg")
        shutil.move(src_path, dst_path)

        dst_path = os.path.join(self.src_files, "test_image_2.jpg")
        src_path = os.path.join(app.config["IMAGE_DETENTION"],"2014","11","22","20141122_154645_det.jpg")
        shutil.move(src_path, dst_path)

        dst_path = os.path.join(self.src_files, "test_image_3.jpg")
        src_path = os.path.join(app.config["IMAGE_DETENTION"],"2014","11","22","20141122_154645_det_1.jpg")
        shutil.move(src_path, dst_path)

        base_path = os.path.join(os.getcwd(), "files")
        shutil.rmtree(base_path)

    def test_run(self):

        test_file_path = os.path.join(self.src_files, "test_image_1.jpg")
        result = indexer.index_jpeg_file(test_file_path)

        test_file_path = os.path.join(self.src_files, "test_image_2.jpg")
        result = indexer.index_jpeg_file(test_file_path)

        self.assertTrue(os.path.exists(result.original_path))
        self.assertTrue(os.path.exists(result.large_path))
        self.assertTrue(os.path.exists(result.thumb_path))
        self.assertTrue(os.path.exists(result.medium_path))
        self.assertEqual(result.links["type"], 1)

        test_file_path = os.path.join(self.src_files, "test_image_3.jpg")
        result = indexer.index_jpeg_file(test_file_path)
        self.assertEqual(result.links["type"], 2)

class TestValidFilename(unittest.TestCase):

    def setUp(self):
        init_paths()
        self.src_files = os.path.join(os.getcwd(), "test_files")

    def tearDown(self):
        db.drop_database(app.config['DB_NAME'])
        shutil.rmtree(self.dst)


    def test_run(self):
        self.dst = os.path.join(os.getcwd(), "get_valid_fileneme")
        os.mkdir(self.dst)

        src = os.path.join(self.src_files, "test_image_1.jpg")
        shutil.copy(src, self.dst)
        shutil.copy(src, os.path.join(self.dst, "test_image.jpg"))
        name = indexer.get_valid_filename(self.dst, "test_image", '.jpg')
        self.assertEquals(name, "test_image_2")


if __name__=='__main__':

    unittest.main()
