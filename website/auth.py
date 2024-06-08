from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, Category, db
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return render_template('home.html', user=current_user)
    if request.method == 'POST':
        email = request.form.get('email') or ''
        password = request.form.get('password') or ''
        user = User.query.filter_by(username = email).first()
        if user != None and user.username == email and user.password == password:            
            flash('LoggedIn succesfully', category="success")     
            login_user(user, remember=True)
            return redirect(url_for('views.home'))           
        else:
            flash('Incorrect Username and Password', category="error")
    return render_template('login.html', user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET','POST'])
def sign_up():
    if current_user.is_authenticated:
        return render_template('home.html', user=current_user)
    if request.method == 'POST':
        email = request.form.get('email') or ''
        first_name = request.form.get('name') or ''
        password1 = request.form.get('password1') or ''
        password2 = request.form.get('password2')
        phone = request.form.get('phone')
        category = int(request.form.get('category') or '0')

        if len(email) >= 4:
            user = User.query.filter_by(username = email).first()
        
        if first_name == None or first_name == '':
            flash('FullName is required', category="error")
        elif phone == None or phone == '':
            flash('Phone No is required', category="error")
        elif len(email) < 4:
            flash('Email must be greater than 4 characters', category="error")
        elif user:
            flash('Email already exists', category="error")
        elif len(password1) < 7:
            flash('Password must be greater than 7 characters', category="error")
        elif password1 != password2:
            flash('Password and ConfirmPassword should match', category="error")
        elif category == 0:
            flash('Please select category', category="error")
        else:
            new_user = User()
            new_user.username = email
            new_user.name = first_name
            new_user.password = password1
            new_user.phone = phone
            new_user.role = 2   # User RoleId = 2
            new_user.categoryid = category
            db.session.add(new_user)
            db.session.commit()
            flash('Account created succesfully', category="success")
            login_user(new_user, remember=True)
            return redirect(url_for('views.home'))

    #categories = Category.query.filter(Category.id != 3).all()
    categories = Category.query.all()
    return render_template('signup.html', user=current_user, categories=categories)