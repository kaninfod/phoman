CREATE TABLE IF NOT EXISTS IMAGES(
  Id INTEGER PRIMARY KEY ,
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
  db_date_taken TEXT,
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

CREATE TABLE IF NOT EXISTS IMAGES (
  Id INTEGER PRIMARY KEY,
  name text

);