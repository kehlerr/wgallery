from wgallery import db, models

try:
    db.drop_all()
    db.create_all()
except:
    exit(-1)
