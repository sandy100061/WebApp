from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    name = db.Column(db.String(150))
    phone = db.Column(db.String(150))
    role = db.Column(db.Integer)
    categoryid = db.Column(db.Integer, db.ForeignKey('category.id'))
    appvisits = db.Column(db.Integer)
    categories = db.relationship('Category')

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)    
    name = db.Column(db.String(150))

class Buspass(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    email = db.Column(db.String(150))
    mobile = db.Column(db.String(150))
    fromdate = db.Column(db.DateTime)
    validity = db.Column(db.DateTime)
    destination = db.Column(db.String(150))
    userid = db.Column(db.Integer, db.ForeignKey('user.id'))
    busrouteid = db.Column(db.Integer, db.ForeignKey('busroute.id'))
    amount = db.Column(db.Float)

class Busroute(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cityname = db.Column(db.String(150))
    price = db.Column(db.Integer)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(150))
    busrouteid = db.Column(db.Integer, db.ForeignKey('busroute.id'))
    addeddate = db.Column(db.DateTime)





