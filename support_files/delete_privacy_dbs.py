import os


for db in os.listdir("./"):
    if "privacy" in db or "log" in db:
        os.remove(db)
