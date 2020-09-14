from flask import render_template, url_for, redirect, flash, request, jsonify
from flask_login import login_user,logout_user, login_required, current_user
from listo_backend_moduals import app
from listo_backend_moduals.forms import RegisterForm, LoginForm
from listo_backend_moduals.models import *
from listo_backend_moduals import bcrypt, login


@app.route("/")
@login_required
def index():
    return render_template("index.html", user =None)


@app.route('/register', methods= ["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegisterForm() #用FlaskWTF初始化資訊為RegisterForm, 以下自動捕捉帳密
    if form.validate_on_submit():
        username = form.username.data
        password = bcrypt.generate_password_hash(form.password.data)
        email = form.email.data
        user = User(username = username,password= password, email = email)
        #print(user, password, email)
        db.session.add(user)
        db.session.commit()
        flash("註冊成功", category="success")
        if request.args.get('next'):
            next_page = request.args.get('next')
            return redirect((url_for(next_page)))
        return redirect(url_for('index'))

    return render_template('register.html',title="Register", form=form)


@app.route('/login', methods = ["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm() #用FlaskWTF初始化資訊為LoginForm
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        remember = form.remember.data
        user = User.query.filter_by(email = email).first() #先用信箱找使用者
        if user and bcrypt.check_password_hash(user.password, password): #確認使用者存在且密碼hash正確
            login_user(user, remember = remember)
            flash("登入成功", category="success")
            if request.args.get('next'):
                next_page = request.args.get('next')
                return redirect(next_page)
            else:
                return redirect(url_for('index'))

        else:
            flash("登入失敗", category="alert")
            render_template('index.html', form=form)
    return render_template('login.html', form =form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect((url_for("login")))
