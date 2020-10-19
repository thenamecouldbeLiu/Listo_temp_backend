from flask import render_template, url_for, redirect, flash, request
from flask_login import login_user,logout_user, login_required, current_user
from listo_backend_moduals import app, photos_settings
from listo_backend_moduals.models import *
from listo_backend_moduals import bcrypt


# ======================================================
# Common
# ======================================================

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
    count = request.values.get('count', type=int)
    page = request.values.get('page', type=int)
    cur_tag = tag.query.filter_by(id=1).order_by(tag.created.desc()).paginate(page, per_page=count, error_out = False).all() #暫以第一個取代
    res = Response(data={"tags" : cur_tag})  # 建立回應實例 (實例內容見model內的Response class)

    if not res.data:
        res.status = 0
        res.msg = "No hot tag was found"
    return res.jsonify_res()

@app.route("/common/get_list/<int:list_id>/", methods=["GET",'POST'])
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
    text = request.values.get('text', type=str)

    cur_tag = tag.query.filter_by(name=text).order_by(tag.created.desc()).all() #暫以第一個取代
    respond = Response(data={"tags" : cur_tag})  # 建立回應實例 (實例內容見model內的Response class)

    if not respond.data:
        respond.status = 0
        respond.msg = "No tag was found"
    return respond.jsonify_res()

  #======================================================
  # Auth
  #======================================================

@app.route("/auth/register/", methods=['GET', "POST"])
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
        user = user(username=name, password=password, email=email, privacy = Authority.Normal_user)
        db.session.add(user)
        db.session.commit()

    return respond.jsonify_res()

@app.route("/auth/login/", methods=['GET', "POST"])
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

@app.route('/auth/logout/', methods=['GET', "POST"])
def Logout():
    logout_user()
    respond = Response()
    return respond.jsonify_res()

  #======================================================
  # User
  #======================================================

@app.route("/user/get_user_lists/", methods=["GET",'POST'])
def GetUserLists():
    data = request.get_json()
    tag_id = data["filter"]
    respond_tags =[]

    for tag in tag_id:
        cur_tag = tag.query.filter_by(id= tag).first()
        respond_tags.append(cur_tag)
    user_list = placeList.query.filter_by(user_id=current_user.id).all()
    respond = Response(data=
                   {"lists": user_list,
                    "tags":respond_tags})

    if not user_list or respond_tags:
        respond.status = 0
        if not user_list:
            respond.msg = "No list was found"
        elif not respond_tags:
            respond.msg = "No list was found"
    return respond.jsonify_res()

@app.route("/user/create_list/", methods=["GET",'POST'])
def CreateList():
    data = request.get_json()
    name = data["name"]
    description = data["description"]
    coverImageURL = data['coverImageURL']
    privacy = data['privacy']
    places = data['places']
    new_list = placeList(name= name, description= description, coverImageURL= coverImageURL, privacy = privacy, places= places, user_id =current_user.id)
    db.session.add(new_list)
    db.session.commit()
    respond = Response(data=
                   {"id": new_list.id})
    return respond.jsonify_res()

@app.route("/user/add_list_places/", methods=["GET",'POST'])
def AddListPlaces():
    data = request.get_json()
    list_id = data["list_id"]
    places = data['places']

    respond = Response()
    if not places or list_id:
        respond.status = 0
        respond.msg = "No place or list was found"

    list_query = placeList.query.filter_by(id=list_id).first()

    for p_id in places:
        place_query = place.query.filter_by(id=p_id).first()
        list_query.place.append(place_query)
        db.session.commit()
    return respond.jsonify_res()


@app.route("/user/remove_list_places/", methods=["GET",'POST'])
def RemoveListPlaces():
    data = request.get_json()
    list_id = data["list_id"]
    places = data['places']

    respond = Response()
    if not places or list_id:
        respond.status = 0
        respond.msg = "No place or list was found"

    list_query = placeList.query.filter_by(id=list_id).first()

    for p_id in places:
        place_query = place.query.filter_by(id=p_id).first()
        list_query.place.remove(place_query)
        db.session.commit()
    return respond.jsonify_res()

@app.route("/user/edit_list/", methods=["GET",'POST'])
def EditList():
    data = request.get_json()
    edit_name = data["name"]
    edit_description = data["description"]
    edit_privacy = data["privacy"]
    edit_coverImageURL = data['coverImageURL']

    cur_list = placeList.query.filter_by(id = current_user.id).first()
    if edit_name:
        cur_list.name = edit_name
    if edit_description:
        cur_list.description = edit_coverImageURL
    if edit_coverImageURL:
        cur_list.coverImageURL = edit_coverImageURL
    if edit_privacy:
        cur_list.privacy = edit_privacy

    respond = Response()
    return respond.jsonify_res()



@app.route("/user/modify_place_tag/", methods=["GET",'POST'])
def ModifyPlaceTag():
    data = request.get_json()
    gmap_id = data["gmap_id"]
    add_tags = data["add"]
    remove_tags = data["remove"]
    new_tag_name = data["newTags"]["name"]
    new_tag_type = data["newTags"]["type"]

    gmap_mark = Mark.query.filter_by(gmap_id = gmap_id).first()
    if not gmap_mark:
        gmap_mark = Mark(gmap_id = gmap_id, latitude = 0, longitude =0) #因為還沒接google API 先暫時建一個值為零

    cur_plcae = place.query.filter_by(gmap_id=gmap_mark.gmap_id).first()
    tag_relationship = tagRelationship.query.filter_by(place_id = cur_plcae.id, user_id = current_user.id).first()
    newTag = tag(name = new_tag_name, type= new_tag_type)
    for t in add_tags:
        newTR = tagRelationship(user_id = current_user.id, tag_id =t, place_id=cur_plcae.id)
        db.session.add(newTR)
        db.session.commit()
    for t in remove_tags:
        tagRelationship.query.filter_by(user_id = current_user.id,tag_id = t).delete()
        db.session.commit()
    new_TR = tag_relationship(user_id = current_user.id, tag_id =newTR.id, place_id=cur_plcae.id)
    db.session.add(newTR)
    db.session.commit()

    #回傳被修改的place, newTag, mark
    respond = Response(data = {
        "modified_place_id":cur_plcae.id,
        "newTag" : newTag.id,
        "mark_id": gmap_mark.gmap_id,
        "mark_longitude":gmap_mark.latitude,
        "mark_latitude":gmap_mark.latitude
    })
    return respond.jsonify_res()


# ======================================================
# Map
# ======================================================

@app.route("/map/get_marks/", methods=["GET",'POST'])
def GetMarks():
    data = request.get_json()
    loc_from = data["from"]
    loc_to = data["to"]
    mark_list = Mark.filter(
        ((Mark.latitude>=loc_from["latitude"]) & (Mark.latitude<=loc_to["latitude"]) & (Mark.latitude>=loc_from["longitude"]) & (Mark.latitude<=loc_to["longitude"]))
    ).all()
    respond = Response(data = {
        "Marks":mark_list
    })
    return respond.jsonify_res()

@app.route("/map/get_place_info/", methods=["GET",'POST'])
def GetPlaceInfo():
    data = request.get_json()
    gmap_id = data['gmap_id']
    cur_place = place.query.filter_by(gmap_id= gmap_id)
    respond = Response(data = {
        "name": cur_place.name,
        "phone": cur_place.phone,
        "address": cur_place.address,
        "type": cur_place.type

    })
    return respond.jsonify_res()

@app.route("/map/get_place_tag/", methods=["GET",'POST'])
def GetPlaceTag():
    data = request.get_json()
    place_id = data["gmap_id"]
    cur_user_tags = tagRelationship.query.filter_by(user_id= current_user.id, place_id = place_id).all()
    tag_list =[]
    for item in cur_user_tags:
        cur_tagid = item.tag_id
        cur_tag = tag.query.filter_by(id = cur_tagid).first()
        tag_list.append(cur_tag)
    respond = Response(data = {
        "tags":tag_list
    })
    return respond.jsonify_res()

@app.route("/map/search_tag/", methods=["GET", 'POST'])
def SearchTag():
    data = request.get_json()
    place_id = data["gmap_id"]
    type = data["type"]
    text = data["text"]

    tags = []
    if place_id:
        cur_tag_rel = tagRelationship.query.filter_by(user_id =current_user.id, place_id = place_id).all()
        for row in cur_tag_rel:
            cur_tag_id = row.tag_id
            cur_tag = tag.query.filter_by(id = cur_tag_id).first()
            tags.append(cur_tag)
    if type:
        cur_tags_type = tag.query.filter_by(type=type).all()
        tags.extend(cur_tags_type)
    if text:
        cur_tags_text = tag.query.filter((tag.type.like("%{}%".format(text))) |
                                         (tag.name.like("%{}%".format(text)))
                                         ).all()
        tags.extend(cur_tags_text)
    respond = Response(data = {
        "tags":tags
    })
    return respond.jsonify_res()

@app.route("/map/candidate_tag/", methods=["GET", 'POST'])
def CandidateTag():
    data = request.get_json()
    gmap_id = data["gmap_id"]
    type_ = data["type"]
    tag_list =[]
    limit_num = data["limit"]
    place_gmapid = place.query.filter_by(gmap_id = gmap_id).all()
    place_type =  place.query.filter_by(type = type_).all()
    tag_list.extend(place_gmapid)
    tag_list.extend(place_type)
    respond = Response(data = {
        "tags":tag_list[:limit_num]
    })
    return respond.jsonify_res()






if __name__ == "__main__":
    user = user.query.filter_by(username = 1).first()
    print(user)