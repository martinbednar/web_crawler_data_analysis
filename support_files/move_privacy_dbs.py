import os
import shutil


for db in os.listdir("./"):
    if "privacy" in db:
        shutil.move(db, "../Crawled_with_uMatrix/" + db)
