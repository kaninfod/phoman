__author__ = 'hingem'
import os
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0, parentdir)

#from app.model import mongo_db
#from app.model.image import image
from app.model.database import Database
from app.model.album import Album

from datetime import timedelta


def main():
    db = Database()
    all_images = db.get_images(query={} ,sort_by="date_taken")
    groups = []

    inteval = 10
    n = timedelta(minutes=inteval)
    min_population = 10
    for rec in all_images:
        date_taken = rec["date_taken"]
        flag = False
        for serie in groups:
            if date_taken < max(serie)+n and date_taken > min(serie)-n:
                serie.append(date_taken)
                flag = True

        if not flag:
            groups.append([date_taken])
    i = 0
    all_dict = []
    for serie in groups:
        if len(serie) > min_population:
            alb = Album()
            alb.startdate = min(serie)
            alb.enddate = max(serie)
            alb.name = str(min(serie))
            alb.type = {
                "value":"time density",
                "min_population":min_population,
                "inteval":inteval,
                "density": (len(serie) / (alb.enddate - alb.startdate)).seconds
            }
            alb.image_count = len(serie)
            alb.save()

        i += 1




    pass

if __name__ == "__main__":
    main()