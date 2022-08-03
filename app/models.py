from collections import UserDict
from lib2to3.pytree import Base
from unicodedata import category
from sqlalchemy import ForeignKey
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import db, login
from flask_login import UserMixin
from hashlib import md5

@login.user_loader
def load_user(id):
    return Users.query.get(int(id))

class Users(db.Model, Base, UserMixin):
    id              = db.Column(db.Integer, primary_key=True)
    email           = db.Column(db.String(100), unique=True, nullable=False)
    password_hash   = db.Column(db.String(150))
    name            = db.Column(db.String(100), nullable=False)
    username        = db.Column(db.String(100), unique=True, nullable=False)
    category        = db.Column(db.Integer, db.ForeignKey('category.id'))
    evaluation      = db.relationship('Evaluation', backref='author', lazy='dynamic')
 
    def set_password(self, password):
       self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)
    
    __mapper_args__ = {
        'polymorphic_identity':'users'
    }
        
class Influencer(Users, UserMixin):
    id              = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)

    def __repr__(self):
        return '<Influencers {}>'.format(self.email)

    __mapper_args__ = {
        'polymorphic_identity':'influencer'
    }

class Business(Users, UserMixin):
    id              = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    location        = db.Column(db.String(200))

    def __repr__(self):
        return '<Business {}>'.format(self.email)

    __mapper_args__ = {
        'polymorphic_identity':'business'
    }

class Evaluation(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    userId          = db.Column(db.Integer, db.ForeignKey('users.id'))
    accEvaluated    = db.Column(db.Integer)
    timestamp       = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    comment         = db.Column(db.String(500))
    rating          = db.Column(db.Integer)
    link            = db.Column(db.String(500))
    complaint       = db.Column(db.String(100))

    def __repr__(self):
        return '<Evaluation {}>'.format(self.rating)

class Category(db.Model):
    id      = db.Column(db.Integer, primary_key=True)
    catg    = db.Column(db.String)
    users   = db.relationship('Users')

    
class Admin(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    email           = db.Column(db.String)
    password_hash   = db.Column(db.String)

    def set_password(self, password):
       self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
