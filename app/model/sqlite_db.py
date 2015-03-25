__author__ = 'hingem'



import sqlite3
from flask import g

DATABASE = 'phoman.db'



def _get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = _connect_to_db()
    return db


def _dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def _connect_to_db():
    con = sqlite3.connect('phoman.db')
    return con

def _execute_sql(sql):
    con = _get_db()
    cursor = con.cursor()
    cursor.execute(sql)
    con.commit()
    return con.total_changes, cursor.lastrowid, cursor

def _initiate_db():

    table_images = """CREATE TABLE IF NOT EXISTS IMAGES(
              _id INTEGER PRIMARY KEY ,
              db_filename TEXT,
              db_original_path TEXT,
              db_large_path TEXT,
              db_medium_path TEXT,
              db_thumb_path TEXT,
              db_size TEXT,
              db_make TEXT,
              db_model TEXT,
              db_ImageUniqueID TEXT,
              db_has_exif TEXT,
              db_date_taken TEXT UNIQUE,
              db_latitude REAL,
              db_longitude REAL,
              db_original_height INTEGER,
              db_original_width INTEGER,
              db_orientation INTEGER,
              db_flash_fired INTEGER,
              db_location INTEGER,
              db_country TEXT,
              db_state TEXT,
              db_address TEXT,
              db_road TEXT

        );
    """

    table_keywords = """CREATE TABLE IF NOT EXISTS KEYWORDS(
              _id INTEGER PRIMARY KEY,
              keyword TEXT UNIQUE

        );
    """

    table_keyword_map = """CREATE TABLE IF NOT EXISTS KEYWORDS_MAP(
              _id INTEGER PRIMARY KEY,
              keyword_id INT,
              image_id INT,
              FOREIGN KEY(keyword_id) REFERENCES KEYWORDS(_id),
              FOREIGN KEY(image_id) REFERENCES IMAGES(_id)

        );
    """


    con = _get_db()


    cursor = con.cursor()
    cursor.execute(table_images)
    con.commit()
    cursor.execute(table_keywords)
    con.commit()
    cursor.execute(table_keyword_map)
    con.commit()

    print()


def save_image(image):
    imgobject = {}
    balcklist =["db_tags", "db_id"]

    update_sql = "UPDATE images\n SET\n"
    insert_sql = "INSERT OR IGNORE INTO\n images\n"
    insert_sql_fields = insert_sql_values = ""


    for field in image.__mongo_attributes__():
        if not field in balcklist:
            imgobject[field] = getattr(image, field)

            update_sql = "%s %s = '%s',    \n" % (update_sql, field, imgobject[field])

            insert_sql_fields = "%s%s,\n" % (insert_sql_fields, field)
            insert_sql_values = "%s'%s',\n" % (insert_sql_values, imgobject[field])


    update_sql = "%s \nWHERE \ndb_date_taken = '%s'" % (update_sql.rstrip().rstrip(","),
                                                        imgobject["db_date_taken"])
    insert_sql = "%s(%s) VALUES (%s)" % (insert_sql,
                                         insert_sql_fields.rstrip().rstrip(","),
                                         insert_sql_values.rstrip().rstrip(","))

    select_updated_sql = "SELECT _id FROM images WHERE db_date_taken = '%s'" % (imgobject["db_date_taken"])
    change, last, cursor = _execute_sql(insert_sql)
    if not change:
        change, last, cursor = _execute_sql(update_sql)
        change, last, cursor = _execute_sql(select_updated_sql)
        image.db_id = cursor.fetchone()[0]
    else:

        image.db_id = last



    for keyword in image.db_tags:
        keyword_id = _insert_keyword(keyword)
        _insert_keyword_mapping(keyword_id, image.db_id)


def _insert_keyword_mapping(keyword_id, image_id):

    sql ="""
        INSERT INTO KEYWORDS_MAP(keyword_id, image_id) VALUES (%s,%s)
    """ % (keyword_id,image_id)

    _execute_sql(sql)

def _insert_keyword(keywords):

    sql_insert_keyword = """
        INSERT INTO KEYWORDS(keyword) VALUES (?)
    """

    con = _get_db()
    cursor = con.cursor()

    try:
        cursor.execute(sql_insert_keyword,(keyword,))
        con.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError as e:
        return _get_keyword(keyword=keyword)


def _get_keyword(id=None, keyword=None):
    if keyword:
        sql_get_keyword = """
            SELECT * FROM KEYWORDS WHERE keyword = ?
        """
        con = _get_db()
        cursor = con.cursor()
        cursor.execute(sql_get_keyword, (keyword,))
        record = cursor.fetchone()
        return record[0]

def get_image(id):

    sql = """
        SELECT * FROM IMAGES WHERE _id = ?
    """

    con = _get_db()
    con.row_factory = _dict_factory
    cursor = con.cursor()
    cursor.execute(sql, (id,))

    record = cursor.fetchone()
    keywords = _get_image_keywords(id)

    record.update({'db_tags':keywords})
    return record


def _get_image_keywords(image_id):

    sql = """
    SELECT (KEYWORDS.keyword)
    FROM images,keywords,keywords_map
    WHERE keywords._id = keywords_map.keyword_id
      AND keyWORDS_MAP.image_id = imaGES._id
      AND images._id = ?
    """

    con = _get_db()

    cursor = con.cursor()
    cursor.execute(sql, (image_id,))

    record = cursor.fetchall()

    return record


