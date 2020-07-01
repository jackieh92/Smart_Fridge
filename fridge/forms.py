from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, EqualTo, Email

class IngredientForm(FlaskForm):
    ingredient_input = StringField("Title", validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    submit = SubmitField()

class UserInfoForm(FlaskForm):
    username = StringField('Username',validators=[DataRequired()])
    email = StringField('Email',validators=[DataRequired(),Email()])
    password = PasswordField('Password',validators=[DataRequired()])
    confirm_pass = PasswordField('Confirm Password',validators =[DataRequired(),EqualTo('password')])
    submit = SubmitField()

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit= SubmitField()

class RecipeSearchForm(FlaskForm):
    ingredient_input_for_recipe = StringField("Title", validators=[DataRequired()])
    submit = SubmitField()