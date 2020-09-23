from flask import render_template, url_for, redirect, flash, request
from flask_login import login_user,logout_user, login_required, current_user
from listo_backend_moduals import app, photos_settings
from listo_backend_moduals.forms import RegisterForm, LoginForm, PostForm
from listo_backend_moduals.models import *
from listo_backend_moduals import bcrypt
import time
import hashlib

@app.route("/", methods=['GET', 'POST'])
@login_required
def index():
    if current_user:
        pages = request.args.get('page', 1, type =int) #從request取的頁面資訊
        posts_in_the_past = Post.query.filter_by(user_id = current_user.id).order_by(Post.timestamp.desc()).paginate(pages,2, False)
    form = PostForm() #初始化為Postform

    if form.validate_on_submit():
        text = form.text.data
        image = form.image.data
        lontitude = form.latitude.data
        latitude = form.lontitude.data
        tagname = form.tag.data
        tagclass = form.tag_class.data
        if image:
            tag = Tag(tagname = tagname, tagclass = tagclass, user_id = current_user.id)
            db.session.add(tag)
            db.session.commit()

            place = Map_Address(lontitude = lontitude, latitude = latitude, user_id = current_user.id, tag = tag.id)
            db.session.add(place)
            db.session.commit()

            name = hashlib.md5(current_user.username + str(time.time()).encode('UTF-8')).hexdigest()[:15] #將上傳檔名以用戶訊息與時間戳記轉為HASH亂碼
            filename = photos_settings.save(image, name = name+'.')
            file_url = photos_settings.url(filename)

            place = Map_Address.query.filter_by(lontitude = lontitude, latitude = latitude).first()
            post = Post(content = text, image_URL = file_url, user_id = current_user.id, address_id = place.id)

            db.session.add(post)
            db.session.commit()
            return redirect(url_for('index'))
        else:

            tag = Tag(tagname=tagname, tagclass=tagclass, user_id=current_user.id)
            db.session.add(tag)
            db.session.commit()
            print("current tag id ="+ str(tag.id))

            place = Map_Address(lontitude=lontitude, latitude=latitude, user_id=current_user.id, tags=tag.id)
            db.session.add(place)
            db.session.commit()

            #place = Map_Address.query.filter_by(lontitude = lontitude, latitude = latitude).first()
            post = Post(content = text, user_id = current_user.id, address_id = place.id)

            db.session.add(post)
            db.session.commit()
            return redirect(url_for('index'))
    return render_template("index.html", form = form, posts_in_the_past = posts_in_the_past)


@app.route('/register', methods= ["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegisterForm() #用FlaskWTF初始化資訊為RegisterForm, 以下自動捕捉帳密
    if form.validate_on_submit():
        username = form.username.data
        password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
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
