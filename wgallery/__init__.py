from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///wgallery_catalogs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '1273912kjshf782y418kjhf8374vjkx'
# app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0 # not for prod
db = SQLAlchemy(app)

from wgallery import routes
from wgallery import models
