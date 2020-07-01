from fridge import app, db
from flask import Flask, render_template, request, redirect, url_for
# import forms
from fridge.forms import IngredientForm, UserInfoForm, LoginForm, RecipeSearchForm
#import models
from fridge.models import Ingredientlist, User, check_password_hash

from flask_login import login_required,login_user,current_user,logout_user

import sqlite3 as sql

import requests
import os


key = os.environ.get('SPOONACULAR_API')

@app.route('/')
def home():
    pasta = requests.get(f'https://api.spoonacular.com/recipes/search?apiKey=d82e2a524d584cd4a578dca7abd8423c&cuisine=italian&number=2')
    testing = pasta.json()
    convert=testing["results"]
      
    
    return render_template("home.html",convert=convert)

# Here we are listing out the recipes by DICT
@app.route('/recipe_list', methods = ['GET', 'POST'])
@login_required
def recipe_list():
    user_id = current_user.id
    current_ingredients = Ingredientlist.query.filter_by(user_id = user_id).all()
    recipe_by_inventory = requests.get(f'https://api.spoonacular.com/recipes/findByIngredients?apiKey=d82e2a524d584cd4a578dca7abd8423c&ingredients={current_ingredients}&number=2')
    convert_request = recipe_by_inventory.json()
    extract_request = convert_request
    print(extract_request)
    recipe_options_dict = {}
    for i in range(len(convert_request)):
        recipe_options_dict[convert_request[i]["id"]] = convert_request[i]["title"]
    return render_template('recipe_list.html', recipe_options_dict=recipe_options_dict )

@app.route('/recipes', methods = ['GET', 'POST'])
@login_required
def get_recipes():
    user_id = current_user.id
    current_ingredients = Ingredientlist.query.filter_by(user_id = user_id).all()

    recipe_by_inventory = requests.get(f'"https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/findByIngredients?apiKey=d82e2a524d584cd4a578dca7abd8423c&ingredients={current_ingredients}&number=1')
    convert_request = recipe_by_inventory.json()
    recipe_title = convert_request[0]["title"]

    # For loop to gather names of items that are in missedIngredients
    missed_ingredients_list = []
    missed_ingredients = convert_request[0]["missedIngredients"]
    for i in range(len(missed_ingredients)):
        missed_ingredients_list.append(missed_ingredients[i]['original'])
        missed_ingredients_string = " ".join(missed_ingredients_list)

    # Here we gather the recipe ID and then call upon Get Analyzed Recipe Instructions DICT
    recipe_id = convert_request[0]["id"]
    get_recipe_steps = requests.get(f'"https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/{recipe_id}/analyzedInstructions?apiKey=d82e2a524d584cd4a578dca7abd8423c&stepBreakdown=false')
    convert_request_steps = get_recipe_steps.json()
    recipe_steps_dict = {}
    recipe_steps = convert_request_steps[0]["steps"]
    for i in range(len(recipe_steps)):
        recipe_steps_dict[recipe_steps[i]["number"]]=recipe_steps[i]["step"]

    # Here we gather the amount and name of each ingredient


    return render_template('recipes.html', recipe_title=recipe_title, missed_ingredients_string=missed_ingredients_string, recipe_steps_dict=recipe_steps_dict)


#Register Route
@app.route('/register', methods=['GET','POST'])
def register():
    form_register = UserInfoForm()
    if request.method == 'POST' and form_register.validate():
        # Get Information
        username = form_register.username.data
        password = form_register.password.data
        email = form_register.email.data
        print("\n",username,password,email)
        # Create an instance of User
        user = User(username,email,password)
        # Open and insert into database
        db.session.add(user)
        # Save info into database
        db.session.commit()
    return render_template('register.html',form_register = form_register)

def is_authenticated(self):
    return True

@app.route('/ingredients', methods = ['GET', 'POST'])
@login_required
def get_ingredients():
    ingredient_form = IngredientForm()
    user_id = current_user.id
    # Showing the list of Ingredients
    updated_items = Ingredientlist.query.filter_by(user_id = user_id).all()
    if request.method == 'POST' and ingredient_form.validate():
        ingredient_adding = ingredient_form.ingredient_input.data
        quantity = ingredient_form.quantity.data
        user_id = current_user.id
        query_items = Ingredientlist.query.filter_by(user_id = user_id).filter_by(ingredient_col = ingredient_adding).first()
        print(query_items)
        if query_items is not None:   
            changing_quantity = query_items.quantity + quantity              
            query_items.quantity = changing_quantity
            query_items.ingredient_adding = ingredient_adding
            query_items.user_id = user_id
            db.session.commit()                
        else:
            # Create an instance of Ingrediant
            ingredient_add = Ingredientlist(ingredient_adding,quantity, user_id)
            # Open and insert into waitlist
            db.session.add(ingredient_add)
            # Save info into database
            db.session.commit()  
    return render_template('ingredients.html', ingredient_form = ingredient_form, updated_items = updated_items)


@app.route('/inventory')
@login_required
def inventory():
    user_id = current_user.id
    query_inventory = Ingredientlist.query.filter_by(user_id = user_id).all()
    return render_template("inventory.html", query_inventory=query_inventory)

@app.route('/ingredient_detail/<int:ingredient_id>')
@login_required
def ingredient_detail(ingredient_id):
    ingredient = Ingredientlist.query.get(ingredient_id)
    return render_template('ingredient_detail.html', ingredient=ingredient)

@app.route('/ingredients/delete/<int:ingredient_id>', methods=['POST'])
@login_required
def ingredient_delete(ingredient_id):
    ingredient = Ingredientlist.query.get(ingredient_id)
    db.session.delete(ingredient)
    db.session.commit()
    return redirect(url_for('inventory'))

#Login
@app.route('/login', methods = ['GET','POST'])
def login():
    form_login = LoginForm()
    if request.method == 'POST' and form_login.validate():
        email = form_login.email.data
        password = form_login.password.data
        logged_user = User.query.filter(User.email == email).first()
        if logged_user and check_password_hash(logged_user.password, password):
            login_user(logged_user)
            return redirect(url_for('home'))
        else:
            return redirect(url_for('login'))
    return render_template('login.html',form_login = form_login)

#Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

