from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


#Import for flask login
from flask_login import LoginManager

import requests
# Create flask app variable
app = Flask(__name__)
app.config.from_object(Config)
url = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/"

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login = LoginManager(app)
login.login_view = 'login' # Specify what page to load for NON-authenticated Users


from fridge import routes,models