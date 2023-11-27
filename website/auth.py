from flask import Blueprint, render_template, request, redirect, url_for, flash
from .mysql_models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from .mysql_models import User
from .neo4j_models import Neo4jHandler
import json


auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user:
            if user.password == password:
                login_user(user, remember=True)
                return redirect(url_for('views.search'))
            else:
                flash('Incorrect password, try again.', category='error')
                return render_template("login.html", user=current_user)
        else:
            flash('Email does not exist.', category='error')
            return render_template("login.html", user=current_user)
    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
            return render_template("signup.html", user=current_user)
        if password != password_confirm:
            flash('Passwords don\'t match.', category='error')
            return render_template("signup.html", user=current_user)
        # Add user to database
        new_user = User(email=email, username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user, remember=True)
        neo4j = Neo4jHandler()
        user_id = current_user.id
        neo4j.create_user_node(user_id)
        
        # Initialize json
        try:
            with open('users.json', 'r') as file:
                users = json.load(file)
        except:
            users = {}

        users[user_id] = {"liked": [], "disliked": [],"subscribed": [], "hit_bell_icon": []}
        with open("users.json", "w") as file:
            json.dump(users, file)
        return redirect(url_for('views.search'))
        
    return render_template("signup.html", user=current_user)