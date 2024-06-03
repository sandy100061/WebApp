from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from sqlalchemy import text
from .models import Note, User, Busroute, Buspass
from . import db
import json
from datetime import datetime
from sqlalchemy import desc
from reportlab.pdfgen import canvas
from flask import send_from_directory
from os import path

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
    busPass = Buspass()    
    busPassId = request.args.get('busPassId')
    destinations = {x.id: x for x in Busroute.query.all()} 
    if busPassId != None:
        busPass = Buspass.query.filter(Buspass.id == busPassId)[0]
        busPass.destination = destinations[busPass.busrouteid].cityname
        busPass.fromdate = busPass.fromdate.date()
        busPass.validity = busPass.validity.date()

    if request.method == 'POST':
        busPassId = request.form.get('passid')
        if busPassId != None:
            amount = float(request.form.get('amount') or '0')
            busPass = Buspass.query.filter(Buspass.id == busPassId)[0]
            todate = request.form.get('renewvalidity') or ''
            if todate == '':
                flash('ToDate is required', category="error")
            else:
                todate = datetime.strptime(todate, '%Y-%m-%d').date()
                sql = text(f'update buspass set validity="{todate}" where id = {busPassId}')
                db.session.execute(sql)
                db.session.commit()   
                flash('Bus Pass Renewed succesfully', category="success")  
        else:
            email = request.form.get('email') or ''
            name = request.form.get('name') or ''
            phone = request.form.get('phone') or ''
            fromDate = request.form.get('fromDate') or ''
            todate = request.form.get('validity') or ''
            destination = request.form.get('destination')
            routeId = int(request.form.get('destination') or '0')
            amount = float(request.form.get('amount') or '0')

            if name == '':
                flash('FullName is required', category="error")
            elif phone == '':
                flash('Phone No is required', category="error")
            elif len(email) < 4:
                flash('Email must be greater than 4 characters', category="error")
            elif fromDate == '':
                flash('FromDate is required', category="error")
            elif todate == '':
                flash('ToDate is required', category="error")
            elif destination == 0:
                flash('Destination is required', category="error")
            busPass = Buspass()  
            busPass.name = name
            busPass.email = email
            busPass.mobile = phone
            busPass.fromdate = datetime.strptime(fromDate, '%Y-%m-%d').date()
            busPass.validity = datetime.strptime(todate, '%Y-%m-%d').date()
            busPass.destination = destination
            busPass.userid = current_user.id
            busPass.busrouteid = routeId
            busPass.amount = amount
            db.session.add(busPass)
            db.session.commit()
            flash('Bus Pass created succesfully', category="success")
            busPasses = Buspass.query.filter(Buspass.userid == current_user.id).order_by(desc(Buspass.id)).all()
            destinations = {x.id: x for x in Busroute.query.all()} 
            totalDays = {}
            for busPass in busPasses:
                busPass.destination = destinations[busPass.busrouteid].cityname     
                totalDays[busPass.id] = getTotalDays(busPass.fromdate, busPass.validity)      

            return render_template('viewpass.html', user=current_user, busPasses = busPasses, totalDays = totalDays)

    routes = Busroute.query.all()
    return render_template('bookpass.html', user=current_user, routes = routes, busPass = busPass)

@views.route('/viewpass', methods=['GET'])
@login_required
def viewpass():       
    busPasses = Buspass.query.filter(Buspass.userid == current_user.id).order_by(desc(Buspass.id)).all()
    destinations = {x.id: x for x in Busroute.query.all()} 
    totalDays = {}
    for busPass in busPasses:
        busPass.destination = destinations[busPass.busrouteid].cityname
        totalDays[busPass.id] = getTotalDays(busPass.fromdate, busPass.validity) 
    return render_template('viewpass.html', user=current_user, busPasses = busPasses, totalDays = totalDays)

def getTotalDays(fromdate:datetime, todate:datetime):
    return (todate - fromdate).days

# @views.route('/downloadpass', methods=['POST'])
# @login_required
# def downloadpass():       
#     c = canvas.Canvas("reportlab_pdf.pdf")
#     c.drawString(100,100,"Hello World")
#     c.showPage()
#     c.save()
#     basedir = path.abspath(path.dirname(__file__))
#     # uploads = os.path.join(current_app.root_path, 'reportlab_pdf.pdf')
#     # send_from_directory(basedir, 'reportlab_pdf.pdf')
#     # flash('PDF downloaded')
#     return jsonify({})