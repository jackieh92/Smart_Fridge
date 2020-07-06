from fridge import app, db, login

#Import for Werkzeug Security
from werkzeug.security import generate_password_hash, check_password_hash

# Import for Date Time Module
from datetime import datetime

from flask_login import UserMixin


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(150), nullable = False, unique = True)
    email = db.Column(db.String(150), nullable = False, unique = True)
    password = db.Column(db.String(256), nullable = False)
    ingredient = db.relationship('Ingredientlist', backref = 'author', lazy = True)
    

    def __init__(self,username,email,password):
        self.username = username
        self.email = email
        self.password = self.set_password(password)

    def set_password(self,password):
        self.pw_hash = generate_password_hash(password)
        return self.pw_hash

    def __repr__(self):
        return f'{self.username} associated with email "{self.email}" has been created.'

class Ingredientlist(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    ingredient_col = db.Column(db.String(200))
    quantity = db.Column(db.Integer, nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    
    def __init__(self,ingredient_col, quantity, user_id):
        self.ingredient_col = ingredient_col
        self.quantity = quantity
        self.user_id = user_id

    def __repr__(self):
            return f'{self.ingredient_col}'

