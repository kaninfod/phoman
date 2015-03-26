__author__ = 'hingem'


from app import db




def save_image(image):

    new_img = image_db().upsert(image)

    for kw in image.db_tags:
        new_kw = keyword_db().upsert(kw)
        keyword_map_db().upsert(keyword_id=new_kw._id, image_id=new_img._id)


class keyword_db(db.Model):
    __tablename__ = 'keyword_db'
    _id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(255), unique=True)

    def upsert(self, keyword):
        kw = self.query.filter_by(keyword=keyword).first()
        if not kw:
            self.keyword = keyword
            db.session.add(self)

        else:
            self._id = kw._id
            self.keyword = kw.keyword

        db.session.commit()
        return self


class keyword_map_db(db.Model):
    __tablename__ = 'keyword_map_db'
    _id = db.Column(db.Integer, primary_key=True)
    keyword_id = db.Column(db.Integer, db.ForeignKey('keyword_db._id'))
    image_id = db.Column(db.Integer, db.ForeignKey('image_db._id'))

    def upsert(self, keyword_id, image_id):
        kw = self.query.filter_by(keyword_id=keyword_id, image_id=image_id).first()
        if not kw:
            self.keyword_id = keyword_id
            self.image_id = image_id
            db.session.add(self)
        db.session.commit()


class image_db(db.Model):
    __tablename__ = 'image_db'
    _id = db.Column(db.Integer, primary_key=True)
    db_filename = db.Column(db.String(255))
    db_original_path = db.Column(db.String(255))
    db_large_path = db.Column(db.String(255))
    db_medium_path = db.Column(db.String(255))
    db_thumb_path = db.Column(db.String(255))
    db_size = db.Column(db.Integer)
    db_make = db.Column(db.String(255))
    db_model = db.Column(db.String(255))
    db_ImageUniqueID = db.Column(db.String(255))
    db_has_exif = db.Column(db.Boolean)
    db_date_taken = db.Column(db.DateTime)
    db_latitude = db.Column(db.Numeric)
    db_longitude = db.Column(db.Numeric)
    db_original_height = db.Column(db.Integer)
    db_original_width = db.Column(db.Integer)
    db_orientation = db.Column(db.Integer)
    db_flash_fired = db.Column(db.Integer)
    db_location = db.Column(db.Boolean)
    db_country = db.Column(db.String(255))
    db_state = db.Column(db.String(255))
    db_address = db.Column(db.String(255))
    db_road = db.Column(db.String(255))


    def upsert(self,image):


        self.db_filename          =   image.db_filename
        self.db_original_path     =   image.db_original_path
        self.db_large_path        =   image.db_large_path
        self.db_medium_path       =   image.db_medium_path
        self.db_thumb_path        =   image.db_thumb_path
        self.db_size              =   image.db_size
        self.db_make              =   image.db_make
        self.db_model             =   image.db_model
        self.db_ImageUniqueID     =   image.db_ImageUniqueID
        self.db_has_exif          =   image.db_has_exif
        self.db_date_taken        =   image.db_date_taken
        self.db_latitude          =   image.db_latitude
        self.db_longitude         =   image.db_longitude
        self.db_original_height   =   image.db_original_height
        self.db_original_width    =   image.db_original_width
        self.db_orientation       =   image.db_orientation
        self.db_flash_fired       =   image.db_flash_fired
        self.db_location          =   image.db_location
        self.db_country           =   image.db_country
        self.db_state             =   image.db_state
        self.db_address           =   image.db_address
        self.db_road              =   image.db_road

        img = self.query.filter_by(db_filename=image.db_filename).first()
        if img:
            self._id = img._id
        else:
            db.session.add(self)
        db.session.flush()

        return self