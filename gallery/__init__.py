from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ponds.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '1273912kjshf782y418kjhf8374vjkx'
# not for prod
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
db = SQLAlchemy(app)

from gallery import routes
from gallery import models
