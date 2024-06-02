from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from sqlalchemy import text
from .models import Note, User, Busroute
from . import db
import json

views = Blueprint('views', __name__)

@views.route('/', methods=['GET','POST'])
@login_required
def home():
    if request.method == 'POST':
        note = Note()
        note.data = request.form.get('note')
        note.user_id = current_user.id
        db.session.add(note)
        db.session.commit()
        flash('Note Added succesfully', category="success")     
    return render_template('home.html', user=current_user)

@views.route('/delete-note', methods=['POST'])
@login_required
def delete_note():  
    note = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})


@views.route('/users', methods=['GET'])
@login_required
def users():       
    users = User.query.filter(User.role != 1).all()
    return render_template('users.html', user=current_user, users = users)

@views.route('/routes', methods=['GET', 'POST'])
@login_required
def routes():       
    if request.method == 'POST':
        cityname = request.form.get('cityname') or ''
        price = request.form.get('price') or ''
        if cityname != '' and price != '':       
            route = Busroute()
            route.cityname = cityname
            route.price = price 
            db.session.add(route)
            db.session.commit()    
            flash('Bus Route created succesfully', category="success")         
        else:
            flash('Please check City Name and Price', category="error")
    routes = Busroute.query.all()
    return render_template('routes.html', user=current_user, routes = routes)

@views.route('/editbusroute', methods=['POST'])
@login_required
def editbusroute():       
    route = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    busid = route['busid']
    cityname = route['cityname'] or ''
    price = route['price'] or ''
    if cityname != '' and price != '':  
        sql = text(f'update busroute set cityname="{cityname}",price={price} where id = {busid}')
        db.session.execute(sql)
        db.session.commit()   
        flash(f'Bus Route {busid} updated succesfully', category="success")         
    else:
        flash('Please check City Name and Price', category="error")
    return jsonify({})


@views.route('/deleteBusRoute', methods=['POST'])
@login_required
def deleteBusRoute():  
    route = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    busid = route['busid']
    busroute = Busroute.query.get(busid)
    if busroute:
       db.session.delete(busroute)
       db.session.commit()
       flash(f'Bus Route {busid} deleted succesfully', category="success")    

    return jsonify({})


@views.route('/bookpass', methods=['GET', 'POST'])
@login_required
def bookpass():       
    if request.method == 'POST':
        flash('Bus Route created succesfully', category="success")         
    else:
        flash('Please check City Name and Price', category="error")
    routes = Busroute.query.all()
    return render_template('bookpass.html', user=current_user, routes = routes)