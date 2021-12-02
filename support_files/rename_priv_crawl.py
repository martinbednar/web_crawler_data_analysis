import os
from zipfile import ZipFile

for archive in os.listdir("./"):
    if "privacy" in archive:
        with ZipFile(archive, 'r') as zip_archive:
            zip_archive.extractall("D:\\Downloads\\Extract")
        
        old_name = archive[0:-4]
        new_name = old_name.replace("_privacy", "") + "_privacy"
        os.rename("D:\\Downloads\\Extract\\" + old_name + ".sqlite", "D:\\Downloads\\Extract\\" + new_name + ".sqlite")
        os.rename("D:\\Downloads\\Extract\\" + old_name + ".log", "D:\\Downloads\\Extract\\" + new_name + ".log")
        
        with ZipFile(new_name + ".zip", 'w') as zip_obj:
            zip_obj.write("D:\\Downloads\\Extract\\" + new_name + ".sqlite", new_name + ".sqlite")
            zip_obj.write("D:\\Downloads\\Extract\\" + new_name + ".log", new_name + ".log")
        
        os.remove(archive)