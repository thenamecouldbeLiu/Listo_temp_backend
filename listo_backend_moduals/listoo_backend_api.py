from flask import render_template, url_for, redirect, flash, request
from flask_login import login_user,logout_user, login_required, current_user
from listo_backend_moduals import app, photos_settings
from listo_backend_moduals.forms import RegisterForm, LoginForm, PostForm
from wtforms.validators import ValidationError
from listo_backend_moduals.models import *
from listo_backend_moduals import bcrypt
import time
import hashlib


@app.route("/common/get_recommand_lists/", methods=['GET', 'POST'])
def GetRecommandLists():
    cur_list = placeList.query.filter_by(id=1).order_by(placeList.created.desc()).all() #暫以第一個取代
    #cur_place = cur_list.place  # 找到place
    respond = Response(data={"lists" : cur_list})  # 建立回應實例 (實例內容見model內的Response class)

    if not cur_list:
        respond.status = 0
        respond.msg = "No recommand list was found"
    return respond.jsonify_res()

@app.route("/common/get_hot_tags/", methods=['GET'])
def GetHotTags():
    count = request.args.get('count', type=int)
    page = request.args.get('page', type=int)
    cur_tag = tag.query.filter_by(id=1).order_by(tag.created.desc()).paginate(page, per_page=count, error_out = False).all() #暫以第一個取代
    res = Response(data={"tags" : cur_tag})  # 建立回應實例 (實例內容見model內的Response class)

    if not res.data:
        res.status = 0
        res.msg = "No hot tag was found"
    return res.jsonify_res()

@app.route("/common/get_list/<int:list_id>/", methods=[ 'POST'])
def GetList():
    data = request.get_json()
    list_id = data["list_id"]
    tag_id = data["filter"]
    respond_places =[]
    respond_tags =[]
    cur_list = placeList.query.filter_by(id=list_id).order_by(placeList.created.desc()).first()
    for place in cur_list.place:
        respond_places.append(place)
    for tag in tag_id:
        cur_tag = tag.query.filter_by(id= tag).first()
        respond_tags.append(cur_tag)


    respond = Response(data=
                   {"tags": respond_tags,
                    "places": respond_places,
                    "info": cur_list})

    if not cur_list:
        respond.status = 0
        respond.msg = "No list was found"
    return respond.jsonify_res()

@app.route("/common/search_tags/", methods=['GET'])
def SearchTags():
    text = request.args.get('text', type=str)

    cur_tag = tag.query.filter_by(name=text).order_by(tag.created.desc()).all() #暫以第一個取代
    respond = Response(data={"tags" : cur_tag})  # 建立回應實例 (實例內容見model內的Response class)

    if not respond.data:
        respond.status = 0
        respond.msg = "No tag was found"
    return respond.jsonify_res()

@app.route("/auth/", methods=['GET', "POST"])
def Auth():
    data = request.get_json()
    email = data["email"]
    name = data["nickname"]
    psw = data["password"]
    password = bcrypt.generate_password_hash(psw).decode('utf-8')
    respond = Response()
    def validate_username(self, username, respond):
        user = user.query.filter_by(username = username.data).first()
        if user:
            respond.status =0
            respond.msg ="Username was taken"
            return False
        return True
    def validate_email(self, user_email, respond):
        email = user.query.filter_by(email = user_email.data).first()
        if email:
            respond.status =0
            respond.msg ="Email was taken"
            return False
        return True

    if validate_email(email, respond) and validate_username(name, respond):
        user = user(username=name, password=password, email=email)
        db.session.add(user)
        db.session.commit()

    return respond.jsonify_res()

@app.route("/login/", methods=['GET', "POST"])
def Login():
    data = request.get_json()
    email = data["email"]
    psw = data["password"]
    user = user.query.filter_by(email=email).first()
    respond = Response()
    if user and bcrypt.check_password_hash(user.password, psw):
        respond.data = {"username": user.username}
        login_user(user)
    else:
        respond.msg = "Not valid"
        respond.status =0
    return respond.jsonify_res()

@app.route('/logout', methods=['GET', "POST"])
def logout():
    logout_user()
    respond = Response()
    return respond.jsonify_res()
