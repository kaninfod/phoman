__author__ = 'hingem'

import os
import shutil
import unittest
from photo_tank.indexer.index_files import index_jpeg_file, get_valid_filename
from photo_tank.app import app



def init_paths():
    base_path = os.path.join(os.getcwd(), "files")
    app.config['TESTING']=True
    app.config['DB_NAME'] = 'test_db'

    app.config["IMAGE_STORE"] = os.path.join(base_path, "image_store")
    app.config["IMAGE_THUMBS"] = os.path.join(base_path, "thumbs")
    app.config["IMAGE_DETENTION"] = os.path.join(base_path, "detention")
    app.config["OTHER_FILES"] = os.path.join(base_path, "other")
    app.config["IMAGE_WATCH_FOLDER"] = os.path.join(base_path, "watch")
    DB_PORT = app.config["DB_PORT"]
    DB_HOST = app.config["DB_HOST"]
    DB_NAME = "test_db"
    app.db.reinitialize(port=DB_PORT, host=DB_HOST, db_name=DB_NAME)

class TestIndexNewFile(unittest.TestCase):


    def setUp(self):
        init_paths()
        self.src_files = os.path.join(os.getcwd(), "test_files")

    def tearDown(self):
        app.db.drop_database(app.config['DB_NAME'])

        src_path = os.path.join(app.config["IMAGE_STORE"],"2014","11","22","20141122_154645.jpg")
        dst_path = os.path.join(self.src_files, "test_image_1.jpg")
        shutil.move(src_path, dst_path)

        base_path = os.path.join(os.getcwd(), "files")
        shutil.rmtree(base_path)

    def test_run(self):

        test_file_path = os.path.join(self.src_files, "test_image_1.jpg")
        self.result = index_jpeg_file(test_file_path)

        self.assertTrue(os.path.exists(self.result.files.original_path))
        self.assertTrue(os.path.exists(self.result.files.large_path))
        self.assertTrue(os.path.exists(self.result.files.thumb_path))
        self.assertTrue(os.path.exists(self.result.files.medium_path))


class TestIndexExistingFile(unittest.TestCase):

    def setUp(self):
        init_paths()
        self.src_files = os.path.join(os.getcwd(), "test_files")


    def tearDown(self):
        app.db.drop_database(app.config['DB_NAME'])

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
        result = index_jpeg_file(test_file_path)

        test_file_path = os.path.join(self.src_files, "test_image_2.jpg")
        self.result = index_jpeg_file(test_file_path)

        self.assertTrue(os.path.exists(result.files.original_path))
        self.assertTrue(os.path.exists(result.files.large_path))
        self.assertTrue(os.path.exists(result.files.thumb_path))
        self.assertTrue(os.path.exists(result.files.medium_path))
        self.assertEqual(result.links["type"], 1)

        test_file_path = os.path.join(self.src_files, "test_image_3.jpg")
        result = index_jpeg_file(test_file_path)
        self.assertEqual(result.links["type"], 2)

class TestValidFilename(unittest.TestCase):

    def setUp(self):
        init_paths()
        self.src_files = os.path.join(os.getcwd(), "test_files")

    def tearDown(self):
        app.db.drop_database(app.config['DB_NAME'])
        shutil.rmtree(self.dst)


    def test_run(self):
        self.dst = os.path.join(os.getcwd(), "get_valid_fileneme")
        os.mkdir(self.dst)

        src = os.path.join(self.src_files, "test_image_1.jpg")
        shutil.copy(src, self.dst)
        shutil.copy(src, os.path.join(self.dst, "test_image.jpg"))
        name = get_valid_filename(self.dst, "test_image", '.jpg')
        self.assertEquals(name, "test_image_2")



class TestAPIAddPhoto(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        IMAGE_STORE = "/Users/hingem/image_server/"
        os.remove(os.path.join(IMAGE_STORE, self.filename))


    def test_run(self):
        self.src_files = os.path.join(os.getcwd(), "test_files")
        test_file_path = os.path.join(self.src_files, "test_image_1.jpg")
        record = {
                    "_id" : "5523d9b3876810b052e188ca",
                    "image_hash" : "0bf5fd07c226e558f96f76676595b0e8",
                    "flash_fired" : 0,
                    "tags" : [
                        {
                            "value" : "November",
                            "category" : "Time"
                        },
                        {
                            "value" : "2014",
                            "category" : "Time"
                        },
                        {
                            "value" : "Saturday",
                            "category" : "Time"
                        },
                        {
                            "value" : "Week 46",
                            "category" : "Time"
                        },
                        {
                            "value" : "Afternoon",
                            "category" : "Time"
                        },
                        {
                            "value" : "Nexus 5",
                            "category" : "Camera"
                        },
                        {
                            "value" : "LGE",
                            "category" : "Camera"
                        },
                        {
                            "value" : "Medium file",
                            "category" : "File"
                        },
                        {
                            "value" : "No Location",
                            "category" : "Location"
                        },
                        {
                            "value" : "Double",
                            "category" : "Indexer"
                        },
                        {
                            "value" : "Double",
                            "category" : "Indexer"
                        },
                        {
                            "value" : "Double",
                            "category" : "Indexer"
                        },
                        {
                            "value" : "Double",
                            "category" : "Indexer"
                        }
                    ],
                    "files" : {
                        "original_path" : "/Users/hingem/image_bank/my_image_store/2014/11/22/20141122_154645.jpg",
                        "original_subpath" : "/Users/hingem/image_bank/my_image_store/2014/11/22",
                        "medium_path" : "/Users/hingem/image_bank/thumbs/2014/11/22/20141122_154645_md.jpg",
                        "filename" : "20141122_154645",
                        "thumb_path" : "/Users/hingem/image_bank/thumbs/2014/11/22/20141122_154645_tm.jpg",
                        "large_path" : "/Users/hingem/image_bank/thumbs/2014/11/22/20141122_154645_lg.jpg",
                        "extension" : ".jpg",
                        "size" : 1344571
                    },
                    "location" : {
                        "road" : None,
                        "latitude" : None,
                        "country" : None,
                        "state" : None,
                        "address" : None,
                        "longitude" : None,
                        "status" : -2,
                        "location" : False
                    },
                    "links" : {
                        "ref" : None,
                        "type" : 1
                    },
                    "original_height" : 2592,
                    "original_width" : 1944,
                    "make" : "LGE",
                    "model" : "Nexus 5",
                    "date_taken" : "2014-11-22T15:46:45.000Z",
                    "has_exif" : True,
                    "orientation" : None,
                    "ImageUniqueID" : None
                }

        from requests import post, get

        res = get('http://localhost:5001/').json()
        url = 'http://localhost:5001/'
        data = {"data":"here"}
        self.filename = record["files"]["filename"] + record["files"]["extension"]
        files = {"file":(self.filename, open(test_file_path,"rb"), 'image/jpeg',{'Expires': '0'})}
        res = post(url, json=record, files=files)
        self.assertEqual(res.status_code, 200)