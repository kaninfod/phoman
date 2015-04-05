__author__ = 'hingem'
import os
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0, parentdir)

from app.model import mongo_db
from datetime import timedelta


def main():
    all_images = mongo_db.get_images(query={} ,sort_by="db_date_taken")
    groups = []

    density = 10
    n = timedelta(minutes=density)
    min_population = 10
    for rec in all_images:
        date_taken = rec["db_date_taken"]
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
            all_dict.append(
                {
                    "startdate": min(serie),
                    "enddate": max(serie),
                    "count": len(serie)
                }
            )
        i += 1



if __name__ == "__main__":
    main()