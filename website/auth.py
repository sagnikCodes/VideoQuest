from flask import Blueprint, render_template, request, redirect, url_for
from .mysql_models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user
from .mysql_models import User
from flask_login import login_required, current_user


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
                return redirect(url_for('views.home'))
            else:
                return render_template("login.html", user=current_user)
        else:
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
            return render_template("signup.html", user=current_user)
        if password != password_confirm:
            return render_template("signup.html", user=current_user)
        # Add user to database
        new_user = User(email=email, username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user, remember=True)
        return redirect(url_for('views.home'))
        
    return render_template("signup.html", user=current_user)