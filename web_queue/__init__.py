from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import Base

from config import Config


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
db.Model = Base
db.create_all()


#from app import routes, models, errors
from web_queue import routes
