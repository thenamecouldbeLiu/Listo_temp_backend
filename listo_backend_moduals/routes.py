from flask import render_template, url_for, redirect, flash, request
from flask_login import login_user,logout_user, login_required, current_user
from listo_backend_moduals import app, photos_settings
from listo_backend_moduals.forms import RegisterForm, LoginForm, PostForm
from listo_backend_moduals.models import *
from listo_backend_moduals import bcrypt
import time
import hashlib
import json
'''@app.route("/", methods=['GET', 'POST'])
@login_required
def index():

    if current_user:
        pages = request.args.get('page', 1, type =int) #從request取得頁面資訊
        query = tagRelationship.query.filter_by(user_id = current_user.id).tag_id #搜尋創建的TAG
        user_tags = query.order_by(tagRelationship.created_time.desc()).all() #排序
        
        #pages = request.args.get('page', 1, type =int) #從request取得頁面資訊
        #user_tags = tagRelationship.query.filter_by(user_id = current_user.id).order_by(tagRelationship.created_time.desc()).paginate(pages,5, False)
    form = PostForm() #初始化為Postform

    if form.validate_on_submit():
        text = form.text.data
        image = form.image.data
        lontitude = form.latitude.data
        latitude = form.lontitude.data
        tagname = form.tag.data
        tagclass = form.tag_class.data
        if image:
            tag = tag(tagname = tagname, tagclass = tagclass, user_id = current_user.id)
            db.session.add(tag)
            db.session.commit()

            place = place(lontitude = lontitude, latitude = latitude, user_id = current_user.id, tag = tag.id)
            db.session.add(place)
            db.session.commit()

            name = hashlib.md5(current_user.username + str(time.time()).encode('UTF-8')).hexdigest()[:15] #將上傳檔名以用戶訊息與時間戳記轉為HASH亂碼
            filename = photos_settings.save(image, name = name+'.')
            file_url = photos_settings.url(filename)

            place = place.query.filter_by(lontitude = lontitude, latitude = latitude).first()

            db.session.add(post)
            db.session.commit()
            return redirect(url_for('index'))
        else:

            tag = tag(tagname=tagname, tagclass=tagclass, user_id=current_user.id)
            db.session.add(tag)
            db.session.commit()
            print("current tag id ="+ str(tag.id))

            place = place(lontitude=lontitude, latitude=latitude, user_id=current_user.id)
            db.session.add(place)
            db.session.commit()


            return redirect(url_for('index'))
    return render_template("index.html", form = form, user_tags = user_tags)




@app.route('/register', methods= ["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegisterForm() #用FlaskWTF初始化資訊為RegisterForm, 以下自動捕捉帳密
    if form.validate_on_submit():
        username = form.username.data
        password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        email = form.email.data
        user = user(username = username,password= password, email = email)
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
        user = user.query.filter_by(email = email).first() #先用信箱找使用者
        if user and bcrypt.check_password_hash(user.password, password): #確認使用者存在且密碼hash正確
            login_user(user, remember = remember) #登入頁的remember checkbox 其值為BOOL 當參數送進前面的REMEMBER 記住此使用者
            # A cookie will be saved on the user’s computer, and then Flask-Login will automatically restore the user ID from that cookie if it is not in the session.
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
    return redirect((url_for("login")))'''
