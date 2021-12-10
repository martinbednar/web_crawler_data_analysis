from zipfile import ZipFile

volume_name = "crawl_60800-60900"

with ZipFile(volume_name + ".zip", 'w') as zip_obj:
    zip_obj.write(volume_name + ".sqlite", volume_name + ".sqlite")
    zip_obj.write(volume_name + ".log", volume_name + ".log")