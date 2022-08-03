import email
from tokenize import String
from typing import Text
from wsgiref.validate import validator
from flask import Flask
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, RadioField, SelectField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from app.models import Category, Influencer, Business

class SearchForm(FlaskForm):
    searched = StringField('Searched', validators=[DataRequired()])
    submit = SubmitField('submit')

class LoginForm(FlaskForm):
    account_type = BooleanField(validators=[DataRequired()])
    email        = StringField('Email', validators=[DataRequired()])
    password     = StringField('Password', validators=[DataRequired()])
    remember_me  = BooleanField('Remember Me')
    submit       = SubmitField('Sign In')

class AdminForm(FlaskForm):
    email        = StringField('Email', validators=[DataRequired()])
    password     = StringField('Password', validators=[DataRequired()])
    submit       = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    account_type = BooleanField(validators=[DataRequired()])
    name         = StringField('Name', validators=[DataRequired()])
    username     = StringField('Username', validators=[DataRequired()])
    category     = SelectField('Category')
    email        = StringField('Email', validators=[DataRequired(), Email()])
    password     = PasswordField('Password', validators=[DataRequired()])
    password2    = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit       = SubmitField('Register')

    if account_type == 'Influencer':
        def validate_username(self, username):
            user = Influencer.query.filter_by(username=username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')

        def validate_email(self, email):
            user = Influencer.query.filter_by(email=email.data).first()
            if user is not None:
                raise ValidationError('Please use a different email address.')

    if account_type == 'Business':
        def validate_username(self, username):
            user = Business.query.filter_by(username=username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')

        def validate_email(self, email):
            user = Business.query.filter_by(email=email.data).first()
            if user is not None:
                raise ValidationError('Please use a different email address.')

class EditProfileForm(FlaskForm):
    name     = StringField('Name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    category = SelectField('Category', validators=[DataRequired()])
    submit   = SubmitField('Submit')

class EvaluationForm(FlaskForm):
    comment     = TextAreaField('Evaluate account', validators=[DataRequired(), Length(min=3, max=200)])
    rating      = RadioField('Rating', choices=[(1,'1 Star'),(2,'2 Stars'),(3,'3 Stars'),(4,'4 Stars'),(5,'5 Stars')], validators=[DataRequired()])
    link        = TextAreaField('Link to post', validators=[DataRequired()])
    complaint   = TextAreaField('Complaint')
    submit      = SubmitField('Submit')

class ReportForm(FlaskForm):
    complaint   = TextAreaField('Complaint')
    submit      = SubmitField('Submit')

