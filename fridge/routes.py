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
    
    return render_template("home.html")

# Here we are listing out the recipes by DICT
@app.route('/recipe_list', methods = ['GET', 'POST'])
@login_required
def recipe_list():
    user_id = current_user.id
    current_ingredients = Ingredientlist.query.filter_by(user_id = user_id).all()
    print(current_ingredients)
    recipe_by_inventory = requests.get(f'https://api.spoonacular.com/recipes/findByIngredients?apiKey={key}&ingredients={current_ingredients}&number=4&ranking=1&ignorePantry=true')
    convert_request_recipe_list = recipe_by_inventory.json()
   
    return render_template('recipe_list.html', convert_request_recipe_list=convert_request_recipe_list)


@app.route('/recipes/<int:recipe_id>', methods = ['GET', 'POST'])
@login_required
def get_recipes(recipe_id):
    user_id = current_user.id

    # Recipe Title
    current_ingredients = Ingredientlist.query.filter_by(user_id = user_id).all()
    recipe_by_inventory = requests.get(f'https://api.spoonacular.com/recipes/{recipe_id}/summary?apiKey={key}')
    convert_request = recipe_by_inventory.json()
    recipe_title = convert_request["title"]

    
    # Here we gather the amount and name of each ingredient
    get_ingredient_names = requests.get(f'https://api.spoonacular.com/recipes/{recipe_id}/ingredientWidget.json?apiKey={key}')
    convert_ingredient_names = get_ingredient_names.json()
    ingredient_names = convert_ingredient_names["ingredients"]
    names = []
    photos = []
    for x in range(len(ingredient_names)):
        names.append(ingredient_names[x]["name"])
        photos.append(ingredient_names[x]["image"])
    spoonacular_string = 'https://spoonacular.com/cdn/ingredients_100x100/'
    appended_photo = [spoonacular_string + image_path for image_path in photos]
    image_name_dict = {names[i]: appended_photo[i] for i in range(len(names))}

    # Display Visuals
    visuals = requests.get(f'https://api.spoonacular.com/recipes/{recipe_id}/information?apiKey={key}&includeNutrition=false')
    convert_visuals = visuals.json()
    display_image = convert_visuals["image"]

    # Here we gather the recipe ID and then call upon Get Analyzed Recipe Instructions DICT
    try:
        get_recipe_steps = requests.get(f'https://api.spoonacular.com/recipes/{recipe_id}/analyzedInstructions?apiKey={key}&stepBreakdown=false')
        convert_request_steps = get_recipe_steps.json()
        recipe_steps_dict = {}
        recipe_steps = convert_request_steps[0]["steps"]
        for i in range(len(recipe_steps)):
            recipe_steps_dict[recipe_steps[i]["number"]]=recipe_steps[i]["step"]
    except:
        return render_template('recipes.html', recipe_title=recipe_title, names=names, display_image=display_image, image_name_dict=image_name_dict)

    return render_template('recipes.html', recipe_title=recipe_title, recipe_steps_dict=recipe_steps_dict, names=names, display_image=display_image, image_name_dict=image_name_dict)

@app.route('/test', methods = ['GET', 'POST'])
@login_required
def test():

    return render_template('test.html' )

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

