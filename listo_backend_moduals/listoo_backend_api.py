from flask import abort, request
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, jwt_refresh_token_required, \
    create_refresh_token, get_jwt_identity
from sqlalchemy.sql import func, desc
from listo_backend_moduals import app, photos_settings
from listo_backend_moduals.models import *
from listo_backend_moduals import bcrypt
import sys
import traceback

# ======================================================
# 回傳錯誤訊息
# ======================================================


def abort_msg(e):
    """500 bad request for exception

    Returns:
        500 and msg which caused problems
    """
    error_class = e.__class__.__name__  # 引發錯誤的 class
    detail = e.args[0]  # 得到詳細的訊息
    cl, exc, tb = sys.exc_info()  # 得到錯誤的完整資訊 Call Stack
    lastcallstack = traceback.extract_tb(tb)[-1]  # 取得最後一行的錯誤訊息
    filename = lastcallstack[0]  # 錯誤的檔案位置名稱
    linenum = lastcallstack[1]  # 錯誤行數
    funcname = lastcallstack[2]  # function 名稱
    # generate the error message
    errmsg = "Exception raise in file: {}, line {}, in {}: [{}] {}. Please contact the member who is " \
             "the person in charge of project!".format(filename, linenum, funcname, error_class, detail)
    # return 500 code
    abort(500, errmsg)

# ======================================================
# Database Model building method
# ======================================================


def push_placeList(name, description, privacy, user_id, coverImageURL, instant_commit=False):

    new_placeList = placeList(name =name, description = description, privacy = privacy, user_id =user_id, coverImageURL
                              =coverImageURL)
    db.session.add(new_placeList)
    if instant_commit:
        db.session.commit()

def push_place(name, latitude, longitude, phone, address, gmap_id, type, system_tag, instant_commit=False):
    new_place = placeList(name =name, latitude = latitude, longitude = longitude, phone =phone, address= address,
                              gmap_id =gmap_id, type= type, system_tag =system_tag)
    db.session.add(new_place)
    if instant_commit:
        db.session.commit()
def push_tag(name, type, instant_commit=False):
    new_tag = placeList(name =name, type = type)
    db.session.add(new_tag)
    if instant_commit:
        db.session.commit()
def push_Mark(gmap_id, latitude, longitude, instant_commit=False):
    new_Mark = placeList(gmap_id = gmap_id, latitude = latitude, longitude = longitude)
    db.session.add(new_Mark)
    if instant_commit:
        db.session.commit()
# ======================================================
# Common
# ======================================================

@app.route("/common/get_recommend_lists/", methods=['GET', 'POST'])
def GetRecommandLists():
    try:
        data = request.get_json()
        if not data.get("filter") or not len(data.get("filter")):
            respond = Response(data={})
            respond.msg = "No filter given"
            respond.status =0
            return respond.jsonify_res()
        list_filter = data["filter"]
        list_query = placeList.query.filter(placeList.id.in_(list_filter)).all() #暫以第一個取代
        res_lists = []  # 找到place
        res_userTags = []
        res_sysTags = []
        temp_placeid = set() #用來查詢的不重複place id
        temp_tagid = set() #用來查詢的不重複tag id
        if len(list_query):
            for list in list_query:
                res_lists.append({
                        "id": list.id,
                        "name": list.name,
                        "description": list.description,
                        "coverImageURL": list.coverImageURL
                    })
                for p in list.place:
                    temp_placeid.add(p.id)
        tagRel_query = tagRelationship.query.filter(tagRelationship.place_id.in_(temp_placeid)).all()
        if len(tagRel_query):
            for relation in tagRel_query:
                temp_tagid.add(relation.tag_id)
            tag_query = tag.query.filter(tag.id.in_(temp_tagid)).all()
            for t in tag_query:
                if t.type==1:
                    res_sysTags.append({"name":t.name})
                else:
                    res_userTags.append({
                        "id":t.id,
                        "name":t.name
                    })


        respond = Response(data={
            "lists" : res_lists,
            "user_tags":res_userTags,
            "system_tags": res_sysTags})  # 建立回應實例 (實例內容見model內的Response class)

        if len(res_lists)==0:
            respond.status = 0
            respond.msg = "No recommend list was found"
        return respond.jsonify_res()
    except Exception as e:
        abort_msg(e)

@app.route("/common/get_hot_tags/", methods=['GET'])
def GetHotTags():
    try:
        count = request.values.get('count', type=int)
        page = request.values.get('page', type=int)
        cur_tag = tag.query.filter_by(id=1).order_by(tag.id).paginate(page, per_page=count, error_out = False) #暫以第一個取代
        res_userTags = []
        res_sysTags = []
        for item in cur_tag.items:
            if item.type==1:
               res_sysTags.append({
                   "id": item.id,
                   "name": item.name
               })
            else:
                res_userTags.append({
                    "id": item.id,
                    "name": item.name

                })
        res = Response(data={
            "user_tags":res_userTags,
            "system_tags": res_sysTags
        })  # 建立回應實例 (實例內容見model內的Response class)
        if len(res_userTags)==0:
            res.status = 0
            res.msg += "No hot user tag was found"
        if len(res_sysTags)==0:
            res.status = 0
            res.msg += "No hot system tag was found"
        return res.jsonify_res()
    except Exception as e:
        abort_msg(e)

@app.route("/common/get_list_info/", methods=["GET",'POST'])
def GetListinfo():
    try:
        data = request.get_json()
        if data.get("list_id"):
            list_id = data["list_id"]
        else:
            list_id = None
        if list_id:
            cur_list = placeList.query.filter_by(id=list_id).first()
            if cur_list:
                respond_list = {
                                       "id": cur_list.id,
                                       "creator_id": cur_list.user_id,
                                       "name": cur_list.name,
                                       "coverImageURL": cur_list.coverImageURL
                }
                user_query = user.query.filter_by(id = cur_list.user_id).first()
                respond_list_info = {
                                       "creator_name": user_query.username,
                                       "privacy": cur_list.privacy,
                                       "description": cur_list.description,
                                       "createdTime": cur_list.created,
                                       "updatedTime": cur_list.updated
                }


        respond = Response(data=
                       {
                        "listinfo": respond_list_info,
                        "list": respond_list
                        })

        if not cur_list:
            respond.status = 0
            respond.msg += "No list was found"
        return respond.jsonify_res()
    except Exception as e:
        abort_msg(e)
@app.route("/common/get_list_detail/", methods=["GET",'POST'])
def GetListDetail():
    try:
        data = request.get_json()
        if data.get("list_id"):
            list_id = data["list_id"]
        else:
            list_id = None
        if data.get("filter"):
            tag_id = data["filter"]
        else:
            tag_id =None
        respond_places =[]
        respond_user_tags =[]
        respond_sys_tags = []
        if list_id:
            cur_list = placeList.query.filter_by(id=list_id).first()
            if cur_list:
                respond_list= {
                                       "id": cur_list.id,
                                       "creator_id": cur_list.user_id,
                                       "name": cur_list.name,
                                       "coverImageURL": cur_list.coverImageURL
                }
                user_query = user.query.filter_by(id = cur_list.user_id).first()
                respond_list_info= {
                                       "creator_name": user_query.username,
                                       "privacy": cur_list.privacy,
                                       "description": cur_list.description,
                                       "createdTime": cur_list.created,
                                       "updatedTime": cur_list.updated
                }

                for item in cur_list.place:
                    respond_places.append({
                        "id": item.id,
                        "name": item.name,
                        "phone": item.phone,
                        "address": item.address,
                        "gmap_id": item.gmap_id,
                        "photo": "UrlStringToBeFilledHere"
                    })
        if tag_id:
            cur_tag = tag.query.filter(tag.id.in_(tag_id)).all()
            for item in cur_tag:
                if item.type == 2:
                    respond_user_tags.append({
                        "id": item.id,
                        "name": item.name
                    })
                if item.type == 1:
                    respond_sys_tags.append({
                        "id": item.id,
                        "name": item.name
                    })


        respond = Response(data=
                       {"user_tags": respond_user_tags,
                        "system_tags": respond_sys_tags,
                        "places": respond_places,
                        "listinfo": respond_list_info,
                        "list": respond_list
                        })

        if not cur_list:
            respond.status = 0
            respond.msg += "No list was found"
        if not data.get("filter") or not len(cur_tag):
            respond.status = 0
            respond.msg += " No tags were found"
        return respond.jsonify_res()
    except Exception as e:
        abort_msg(e)

@app.route("/common/search_tags/", methods=['GET', 'POST'])
def SearchTags():
    try:
        #data = request.get_json()
        content = request.values.get('text', type=str)
        if not content:
            respond = Response(data={})
            respond.status = 0
            respond.msg = "No text given"
            return respond.jsonify_res()
        #content = data["text"]


        cur_tag = tag.query.filter(tag.name.like("%{}%".format(content))).all()
        respond_tags =[]
        for item in cur_tag:
            respond_tags.append({
                "id": item.id,
                "name": item.name
                })


        respond = Response(data={"tags" : respond_tags})  # 建立回應實例 (實例內容見model內的Response class)

        if not len(cur_tag):
            respond.status = 0
            respond.msg = "No tag was found"
        return respond.jsonify_res()
    except Exception as e:
        abort_msg(e)

  #======================================================
  # Auth
  #======================================================

@app.route("/auth/register/", methods=['GET', "POST"])
def register():
    try:
        data = request.get_json()
        email = data["email"]
        username = data["username"]
        psw = data["password"]
        password = bcrypt.generate_password_hash(psw).decode('utf-8')
        respond = Response(data = {})
        def validate_username(respond):
            User = user.query.filter_by(username = username).first()
            if User:
                respond.status =0
                respond.msg ="Username was taken"
                return False
            return True
        def validate_email(email):
            email = user.query.filter_by(email = email).first()
            if email:
                respond.status =0
                respond.msg ="Email was taken"
                return False
            return True

        if validate_email(email) and validate_username(username):
            User = user(username=username, password=password, email=email, privacy = Authority.Normal_user)
            db.session.add(User)
            db.session.commit()

        return respond.jsonify_res()
    except Exception as e:
        abort_msg(e)

@app.route("/auth/login/", methods=['GET', "POST"])
def Login():
    try:
        data = request.get_json()
        email = data["email"]
        psw = data["password"]
        User = user.query.filter_by(email=email).first()

        respond = Response(data={})
        if User and bcrypt.check_password_hash(User.password, psw):
            access_token = create_access_token(identity=User.id, fresh=True)
            respond.msg = "Logged in"
            respond.data = {"user_id": User.id,
                            "username": User.username,
                            "access_token": access_token,
                            'refresh_token': create_refresh_token(identity=User.id)
                            }
            #login_user(User)
        else:
            respond.msg = "Not valid"
            respond.status =0
        return respond.jsonify_res()
    except Exception as e:
        abort_msg(e)

@app.route('/auth/refresh/', methods=['GET','POST'])
@jwt_refresh_token_required
def refresh():
    try:
        current_user_id = get_jwt_identity()

        respond = Response(data={})
        respond.data = {"user_id": current_user_id,
                        'refreshed_access_token': create_access_token(identity=current_user_id, fresh=False)
                        #不給fresh token(因為未重新登入) 可保護某些重要page要重新登入才可瀏覽
                        }
        return respond.jsonify_res()
    except Exception as e:
        abort_msg(e)

"""@app.route("/auth/fresh_login/", methods=['GET', "POST"])
def Fresh_Login():
    try:
        data = request.get_json()
        email = data["email"]
        psw = data["password"]
        User = user.query.filter_by(email=email).first()

        respond = Response(data={})
        if User and bcrypt.check_password_hash(User.password, psw):
            access_token = create_access_token(identity=User.id, fresh=True)
            respond.msg = "Fresh Logged in"
            respond.data = {"user_id": User.id,
                            "access_token":access_token,
                            }
            #login_user(User)
        else:
            respond.msg = "Not valid"
            respond.status =0
        return respond.jsonify_res()
    except Exception as e:
        abort_msg(e)"""
#log out of JWT needs to be rewriten
#need to implement jwt expire
"""@app.route('/auth/logout/', methods=['GET'])
def Logout():
    try:
        respond = Response(data={"username": current_user.username})
        respond.msg ="User logged out"
        logout_user()
        return respond.jsonify_res()
    except Exception as e:
        abort_msg(e)"""

  #======================================================
  # User
  #======================================================

@app.route("/user/get_user_places/", methods=["GET",'POST'])
@jwt_required
def GetUserPlaces():
    try:
        data = request.get_json()
        filter_ = data["filter"]
        current_user_id = get_jwt_identity()
        current_user = user.query.filter_by(id = current_user_id).first()
        current_user_list = current_user.placelist

        temp_places =[]
        temp_tags =set()

        places_with_filter_tags = []
        user_tags_of_userlist = []
        sys_tags_of_userlist = []

        for l in current_user_list:
            for p in l.place:
                t_rel = tagRelationship.query.filter(tagRelationship.user_id==current_user_id,
                                             tagRelationship.tag_id.in_(filter_),
                                             tagRelationship.place_id==p.id).all()
                for item in t_rel:
                    temp_places.append(item.place_id)
                    temp_tags.add(item.tag_id)

        respond_all_places = place.query.filter(place.id.in_(temp_places)).all()

        for p in respond_all_places:
            places_with_filter_tags.append({
                "id": p.id,
                "gmap_id": p.gmap_id,
                "name": p.name,
                "phone": p.phone
            })

        respond_all_tag = tag.query.filter(tag.id.in_(temp_tags)).all()
        for t in respond_all_tag:
            if t.type ==1:
                sys_tags_of_userlist.append({
                    "id": t.id,
                    "name": t.name
                })
            if t.type == 2:
                user_tags_of_userlist.append({
                    "id": t.id,
                    "name": t.name
                })

        respond = Response(data=
                       {"places": places_with_filter_tags,
                        "user_tags": user_tags_of_userlist,
                        "system_tags": sys_tags_of_userlist
                        })

        if not len(places_with_filter_tags) or not len(user_tags_of_userlist) or not len(sys_tags_of_userlist):
            respond.status = 0
        if not len(places_with_filter_tags):
            respond.msg += "No lists was found"
        if not len(user_tags_of_userlist):
            respond.msg += " No User_Tag was found"
        if not len(sys_tags_of_userlist):
            respond.msg += " No system_Tag was found"

        return respond.jsonify_res()
    except Exception as e:
        abort_msg(e)


@app.route("/user/get_user_lists/", methods=["GET",'POST'])
@jwt_required
def GetUserLists():
    try:
        data = request.get_json()
        filter_ = data["filter"]
        current_user_id = get_jwt_identity()
        current_user = user.query.filter_by(id = current_user_id).first()
        #用set實作 先找關聯 再找place相關的tag 記錄下來
        user_tags_of_userlist = [] #最後要回傳ㄉusertags
        sys_tags_of_userlist = [] #最後要回傳ㄉsystem tags
        list_with_filter_tags = []  # 最後要回傳的list

        temp_tag_place_list =set() #有filter裡面tag的place
        temp_all_tags =set()

        for l in current_user.placelist:
            for p in l.place:
                tag_place_qeury = tagRelationship.query.filter_by(place_id = p.id, user_id=current_user.id).all()
                for relation in tag_place_qeury:
                    if relation.tag_id in filter_: #找到關聯後如果該list有tag在filter裡面>放入set
                        temp_tag_place_list.add(l.id)

                    temp_all_tags.add(relation.tag_id) #這個list l 裡面的place p 所有的tag

        cur_tags = tag.query.filter(tag.id.in_(temp_all_tags)).all()
        for t in cur_tags:
            if t.type == 2:
                user_tags_of_userlist.append({
                    "id":t.id,
                    "name":t.name
                })
            if t.type == 1:
                sys_tags_of_userlist.append(
                    {
                        "id": t.id,
                        "name":t.name
                    }
                )

        all_list = placeList.query.filter(placeList.id.in_(temp_tag_place_list)).all() #所有有filter tags在裡面的lists
        for query_list in all_list:
            if query_list.pricacy ==1:
                list_with_filter_tags.append(query_list.get_list())

        respond = Response(data=
                       {"lists": list_with_filter_tags,
                        "user_tags": user_tags_of_userlist,
                        "system_tags":sys_tags_of_userlist
                        })

        if not len(list_with_filter_tags) or not len(user_tags_of_userlist) or not len(sys_tags_of_userlist):
            respond.status= 0
        if not len(list_with_filter_tags):
            respond.msg += "No lists was found"

        if not len(user_tags_of_userlist):
            respond.msg += " No User_Tag was found"

        if not len(sys_tags_of_userlist):
            respond.msg += " No system_Tag was found"

        return respond.jsonify_res()
    except Exception as e:
        abort_msg(e)


@app.route("/user/create_list/", methods=["GET",'POST'])
@jwt_required
def CreateList():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        if data.get("name"):
            name = data["name"]
        else:
            name =""
        if data.get("description"):
            description = data["description"]
        else:
            description = ""
        if data.get("privacy"):
            privacy = data['privacy']
        else:
            privacy = 2
        new_list = placeList(name= name, description= description, privacy = privacy,  user_id =current_user_id)

        #加入地點
        if data.get("places"):
            places = data['places']
            place_query = place.query.filter(place.id.in_(places)).all()
            for p in place_query:
                new_list.place.append(p)
            db.session.add(new_list)
            db.session.commit()

        respond = Response(data=
                       {
                           "list_id": new_list.id
                       })
        return respond.jsonify_res()
    except Exception as e:
        abort_msg(e)

@app.route("/user/set_list_cover/", methods=["GET",'POST'])
@jwt_required
def SetListCover():
    try:
        data = request.get_json()
        if data.get("list_id"):
            list_id = data["list_id"]
        else:
            respond = Response(data = {})
            respond.msg = "NO list id given"
            respond.status = 0
            return respond.jsonify_res()
        if data.get("cover_image_url"):
            cover_image_url = data["cover_image_url"]
        else:
            respond = Response(data = {})
            respond.msg = "NO cover_image_url given"
            respond.status = 0
            return respond.jsonify_res()
        list_query = placeList.query.filter_by(id = list_id).first()
        list_query.coverImageURL = cover_image_url
        respond = Response(data=
                       {"list_id": list_id,
                        "cover_URL":cover_image_url})
        return respond.jsonify_res()

    except Exception as e:
        abort_msg(e)


@app.route("/user/search_user_places/", methods=["GET", 'POST'])
@jwt_required
def SearchUserPlaces():
    try:
        data = request.get_json()
        if data.get("list_id"):
            list_id = data["list_id"]
        else:
            respond = Response(data = {})
            respond.msg = "NO list id given"
            respond.status = 0
            return respond.jsonify_res()
        if data.get("text"):
            content = data["text"]
        else:
            respond = Response(data = {})
            respond.msg = "NO text given"
            respond.status = 0
            return respond.jsonify_res()

        list_query = placeList.query.filter_by(id =list_id).first()
        temp_place_storage_list = [] #從list裡面找到的地點
        temp_place_storage_text = [] #從text裡面找到的地點
        place_query = place.query.filter(place.name.like("%{}%".format(content))).all()
        for p in list_query.place:
            #把list裡面的place裝進[] (因為list.place給的是place的實例)
            temp_place_storage_list.append(p.id)
        for k in place_query:
            #挑出place_query中不在清單的地點
            if k.id not in temp_place_storage_list:
                temp_place_storage_text.append({
                    "id":k.id,
                    "gmap_id": k.gmap_id,
                    "name":k.name,
                    "phone":k.phone
                })



        respond = Response(data=
                           {"places": temp_place_storage_text})
        if not len(temp_place_storage_text):
            respond.status = 0
            respond.msg = "No place was found"
        return respond.jsonify_res()

    except Exception as e:
        abort_msg(e)


@app.route("/user/add_list_places/", methods=["GET",'POST'])
@jwt_required
def AddListPlaces():
    try:

        data = request.get_json()

        if not data.get("list_id"):
            respond = Response(data={})
            respond.status = 0
            respond.msg = "No list_id given"
            return respond.jsonify_res()

        if not data.get("places"):
            respond = Response(data={})
            respond.status = 0
            respond.msg = "No places given"
            return respond.jsonify_res()

        list_id = data["list_id"]
        places = data['places']

        respond = Response(data ={})

        list_query = placeList.query.filter_by(id=list_id).first()

        place_query = place.query.filter(place.id.in_(places)).all()
        for p in place_query:
            list_query.place.append(p)
        db.session.commit()
        if not len(place_query):
            respond.status = 0
            respond.msg = "No place found"
        if not list_query:
            respond.status = 0
            respond.msg += "No placeList was found"
        return respond.jsonify_res()

    except Exception as e:
        abort_msg(e)


@app.route("/user/remove_list_places/", methods=["GET",'POST'])
@jwt_required
def RemoveListPlaces():
    try:
        data = request.get_json()

        if not data.get("list_id"):
            respond = Response(data={})
            respond.status = 0
            respond.msg = "No list_id given"
            return respond.jsonify_res()

        if not data.get("places"):
            respond = Response(data={})
            respond.status = 0
            respond.msg = "No places given"
            return respond.jsonify_res()

        list_id = data["list_id"]
        places = data['places']

        respond = Response(data={})

        list_query = placeList.query.filter_by(id=list_id).first()
        #print(list_query.place)
        #用雙迴圈是因為移除地點後 generator給的list不同 所以要重新跑一次
        #而且place不一定是sorted的 只能重新跑 (除非加入時排序)
        if len(list_query.place):
            for p_id in places: #要移除的place
                for p in list_query.place: #清單原本的place
                    if p.id == p_id:
                        list_query.place.remove(p)
                        break
            db.session.commit()
        if not list_query:
            respond.status = 0
            respond.msg += "No placeList was found"
        return respond.jsonify_res()

    except Exception as e:
        abort_msg(e)

@app.route("/user/edit_list/", methods=["GET",'POST'])
@jwt_required
def EditList():
    try:
        data = request.get_json()
        if data.get("list_id"):
            cur_list = data["list_id"]
        else:
            respond = Response(data={})
            respond.status = 0
            respond.msg = "No list id given"
            return respond.jsonify_res()

        if data.get("name"):
            edit_name = data["name"]
        else:
            edit_name =None
        if data.get("description"):
            edit_description = data["description"]
        else:
            edit_description = None
        if data.get("privacy"):
            edit_privacy = data["privacy"]
        else:
            edit_privacy = None
        if data.get("coverImageURL"):
            edit_coverImageURL = data['coverImageURL']
        else:
            edit_coverImageURL =None

        cur_list_query = placeList.query.filter_by(id = cur_list).first()
        if cur_list_query:
            if edit_name:
                cur_list_query.name = edit_name
            if edit_description:
                cur_list_query.description = edit_description
            if edit_coverImageURL:
                cur_list_query.coverImageURL = edit_coverImageURL
            if edit_privacy:
                cur_list_query.privacy = edit_privacy

            respond = Response(data={})
        else:
            respond = Response(data={})
            respond.msg = "List not found"
            respond.status =0
        return respond.jsonify_res()
    except Exception as e:
        abort_msg(e)


@app.route("/user/modify_place_tag/", methods=["GET",'POST'])
@jwt_required
def ModifyPlaceTag():
    try:
        import random
        import string
        current_user_id = get_jwt_identity()
        current_user = user.query.filter_by(id = current_user_id).first()
        def get_random_string(length):
            letters = string.ascii_lowercase
            result_str = ''.join(random.choice(letters) for i in range(length))
            return result_str
        data = request.get_json()
        if data.get("place_id"):
            place_id = data["place_id"]
        else:
            respond = Response(data={})
            respond.msg = "no place id given"
            respond.status = 0
            return respond.jsonify_res()

        if data.get("add"):
            add_tags = data["add"]
        else:
            add_tags =[]

        if data.get("remove"):
            remove_tags = data["remove"]
        else:
            remove_tags = []

        if data.get("newTags"):
            newTags = data["newTags"]
        else:
            newTags = []


        """place_query = place.query.filter_by(place_id = place_id).first()
        if not place_query:
            # 因為還沒接google API 先丟隨機值

            gmap_mark = Mark(latitude =random.uniform(-100, 100),longitude = random.uniform(-100, 100))
            db.session.add(gmap_mark)

            db.session.commit()"""

        cur_plcae = place.query.filter_by(id=place_id).first()
        if not cur_plcae:
            gmap_mark = Mark(latitude =random.uniform(-100, 100),longitude = random.uniform(-100, 100))
            db.session.add(gmap_mark)
            db.session.commit()

            #這邊要先接google API 回傳地點資訊後再新建 暫時以隨機值代替
            #print("place erro")
            cur_plcae = place(
                name=get_random_string(8),
                latitude =random.uniform(-100, 100), # 緯度<float>
                longitude = random.uniform(-100, 100), # 經度<float>
                phone = get_random_string(8),
                address = get_random_string(8),
                gmap_id = gmap_mark.gmap_id,
                type = "temptype"
            )

            db.session.add(cur_plcae)
            db.session.commit()

        if len(add_tags):
            add_tag_query = tagRelationship.query.filter(tagRelationship.user_id == current_user.id,
                                                         tagRelationship.tag_id.in_(add_tags),
                                                         tagRelationship.place_id == cur_plcae.id).all()
            tag_check_list =[] #放找到的tagid
            for q in add_tag_query:
                tag_check_list.append(q.tag_id)
            for t in add_tags: #place新增原有的tag
                if t not in tag_check_list:
                    newTR = tagRelationship(user_id = current_user.id, tag_id =t, place_id=cur_plcae.id)
                    db.session.add(newTR)

        if len(remove_tags):
            for t in remove_tags:#placeg刪除原有的tag
                tagRelationship.query.filter_by(user_id = current_user.id,tag_id = t, place_id=cur_plcae.id).delete()


        respond_new_tags =[]
        for item in newTags:
            #newTag = tag(name = item['name'], type= item['type']) #新增tag
            newTag = tag(name=item, type=2)
            db.session.add(newTag)
        db.session.commit()


        for t in respond_new_tags:
            if not tagRelationship.query.filter_by(place_id=cur_plcae.id, user_id=current_user.id, tag_id=t).first():
                tag_relationship = tagRelationship(place_id=cur_plcae.id, user_id=current_user.id, tag_id=t)
                #如果沒有該關聯 新增place tag user關聯
                db.session.add(tag_relationship)
        db.session.commit()

        respond = Response(data = {})
        """"modified_place_id":cur_plcae.id,
        "newTag" : respond_new_tags,
        "mark_id": gmap_mark.gmap_id,
        "mark_longitude":gmap_mark.latitude,
        "mark_latitude":gmap_mark.latitude,
        "new_plcae": cur_plcae.id"""

        return respond.jsonify_res()
    except Exception as e:
        abort_msg(e)

@app.route("/user/search_tag/", methods=["GET", 'POST'])
@jwt_required
def SearchTag():
    try:
        data = request.get_json()
        if data.get("place_id"):
            place_id = data["place_id"]
        else:
            respond = Response(data={})
            respond.msg = "no place id given"
            respond.status = 0
            return respond.jsonify_res()


        if data.get("text"):
            content = data["text"] #搜尋的關鍵字
        else:
            respond = Response(data={})
            respond.msg = "no text given"
            respond.status = 0
            return respond.jsonify_res()
        current_user_id = get_jwt_identity()
        tags = [] #要回傳的tags

        if place_id:
            temp_tag_list = []
            cur_tag_rel = tagRelationship.query.filter_by(user_id =current_user_id, place_id = place_id).all()
            for row in cur_tag_rel:
                temp_tag_list.append(row.tag_id)
            tag_query = tag.query.filter(tag.id.in_(temp_tag_list)).all()
        if len(content):
            for t in tag_query:
                #如果tag是公開的 且名字裡面有text
                if content in t.name and t.type == 2:
                    tags.append({
                        "name": t.name,
                        "id": t.id
                    })
        else:
            #搜尋使用者前三名使用的tag 依照使用次數排序

            tag_rel_query = tagRelationship.query.with_entities(tagRelationship.tag_id, func.count(
                tagRelationship.tag_id)).filter_by(user_id=current_user_id).group_by(tagRelationship.tag_id,
                                                                                     tagRelationship.user_id).\
                having(func.count
                (tagRelationship.tag_id) >= 1).order_by(desc(func.count(tagRelationship.tag_id))).limit(3).all()

            tags =[] #回傳的tag陣列
            if len(tag_rel_query):
                for t in tag_rel_query:
                    print( "tag_id:", t.tag_id)
                    tag_query.append(t.tag_id)
                tag_query = tag.query.filter(tag.id.in_(tag_query)).all()
                #print(tag_query)
                for t in tag_query:
                    tags.append({
                        "name": t.name,
                        "id": t.id
                    })
        respond = Response(data={
            "tags": tags
        })
        if not len(tags):
            respond.msg = "No tag was found"
            respond.status = 0
        return respond.jsonify_res()
    except Exception as e:
        abort_msg(e)


@app.route("/user/get_place_tags/", methods=["GET", 'POST'])
@jwt_required
def GetPlaceTags():
    try:
        data = request.get_json()
        if data.get("place_id"):
            place_id = data["place_id"]
        else:
            respond = Response(data={})
            respond.msg = "no place id given"
            respond.status = 0
            return respond.jsonify_res()
        current_user_id = get_jwt_identity()
        cur_place_tags = [] #最後回傳的tags
        place_related_tags =[]

        #找tagRelationship
        cur_place_rel = tagRelationship.query.filter_by(user_id = current_user_id, place_id = place_id).all()
        all_cur_place_rel = tagRelationship.query.filter_by(place_id = place_id).all()
        #暫存tag_id
        temp_tag_list =[]
        for rel in cur_place_rel:
            temp_tag_list.append(rel.tag.id)
        #用in_反找tag
        tag_query = tag.query.filter(tag.id.in_(temp_tag_list)).all()
        for t in tag_query:
            cur_place_tags.append({
                "id": t.id,
                "name": t.name
            })
        for rel in all_cur_place_rel:
            place_related_tags.append(rel.tag_id)
        all_place_related_tags_query = tag.query.filter(tag.id.in_(place_related_tags)).all()
        related_tags =[]
        for t in all_place_related_tags_query:
            if t.type == 1:
                related_tags.append(
                    {
                        "id": t.id,
                        "name":t.name
                    }
                )
        respond = Response(data = {
            "place_tags": cur_place_tags,
            "related_tags": related_tags
        })
        if not len(cur_place_tags):
            respond.msg += "No tag was found in the place"
            respond.status =0
        if not len(all_place_related_tags_query):
            respond.msg += "No related tag found related to the place"
            respond.status =0
        return respond.jsonify_res()


    except Exception as e:
        abort_msg(e)

@app.route("/user/send_tag_event/", methods=["GET", 'POST'])
@jwt_required
def SendTagEvent():
    try:
        data = request.get_json()
        respond = Response(data={})
        if data.get("tag_id"):
            tag_id = data["tag_id"]
        else:
            respond.status = 0
            respond.msg +="No tag id given"
        if data.get("tag_events"):
            tag_events = data["tag_events"]
        else:
            respond.status = 0
            respond.msg +="No tag event given"
        if not respond.status:
            return respond.jsonify_res()

        current_user_id = get_jwt_identity()
        current_user = user.query.filter_by(id = current_user_id).first()
        current_user.pushTagEvent(tag_id= tag_id, events= tag_events)

        respond.data = {"current tag events":current_user.getTagEvent(tag_id)}
        if not current_user.getTagEvent(tag_id):
            respond.msg = "No event was found"
            respond.status =0

        return respond.jsonify_res()


    except Exception as e:
        abort_msg(e)

# ======================================================
# Map
# ======================================================

@app.route("/map/get_marks/", methods=["GET",'POST'])
def GetMarks():
    try:
        data = request.get_json()
        loc_from = data["from"]
        loc_to = data["to"]
        mark_list = Mark.query.filter(
            ((Mark.latitude>=loc_from["latitude"]) & (Mark.latitude<=loc_to["latitude"]) &
             (Mark.longitude>=loc_from["longitude"]) & (Mark.longitude<=loc_to["longitude"]))
        ).all()
        respond_mark_list = {}
        for item in mark_list:
            respond_mark_list[item.gmap_id] = {
                "latitude" : item.latitude,
                "longtitude" : item.longitude
            }
        mark_id_list = respond_mark_list.keys()
        place_query = place.query.filter(place.gmap_id.in_(mark_id_list)).all()
        user_tag_query = []
        sys_tag_query = []
        temp_query =[]
        temp_place_id_list = []
        for p in place_query:
            temp_place_id_list.append(p.id)
        tagRel_query = tagRelationship.query.filter(tagRelationship.place_id.in_(temp_place_id_list)).all()

        for rel in tagRel_query:
            temp_query.append(rel.tag_id)

        tag_query = tag.query.filter(tag.id.in_(temp_query)).all()
        for t in tag_query:
            if t.type==2:
                user_tag_query.append({
                    "id":t.id,
                    "name":t.name
                })
            if t.type==1:
                sys_tag_query.append(
                    {
                        "id": t.id,
                        "name": t.name
                    }
                )



        respond = Response(data = {
            "Marks":respond_mark_list, #回傳gmap_id的array
            "user_tags":user_tag_query,
            "system_tags":sys_tag_query
        })
        return respond.jsonify_res()
    except Exception as e:
        abort_msg(e)

@app.route("/map/get_place_info/", methods=["GET",'POST'])
def GetPlaceInfo():
    try:
        data = request.get_json()
        if not data.get("place_id"):
            respond = Response(data={})
            respond.msg = "No place_id id given"
            respond.status = 0
            return respond.jsonify_res()

        place_id = data['place_id']
        cur_place = place.query.filter_by(id= place_id).first()
        if cur_place:
            respond = Response(data = {
                "name": cur_place.name,
                "phone": cur_place.phone,
                "address": cur_place.address,
                "type": cur_place.type

            })
        else:
            respond = Response(data = {})
            respond.msg ="No mark was found"
            respond.status = 0
        return respond.jsonify_res()
    except Exception as e:
        abort_msg(e)

@app.route("/map/get_place_tag/", methods=["GET",'POST'])
def GetPlaceTag():
    try:
        data = request.get_json()
        place_id = data["gmap_id"]
        current_user_id = get_jwt_identity()
        current_user = user.query.filter_by(id = current_user_id).first()
        cur_user_tags = tagRelationship.query.filter_by(user_id= current_user.id, place_id = place_id).all() #用currentuser.id跟place_id找 relationship
        temp_tag_list=[]
        tags = [] #回應的tag_list
        for item in cur_user_tags:
            temp_tag_list.append(item.tag_id)

        if len(temp_tag_list):
            tag_query = tag.query.filter(tag.id.in_(temp_tag_list)).all()
            for t in tag_query:
                tags.append({
                    "name":t.name,
                    "id" : t.id
                })
        respond = Response(data = {
            "tags":tags
        })
        return respond.jsonify_res()
    except Exception as e:
        abort_msg(e)






if __name__ == "__main__":
    user = user.query.filter_by(username = 1).first()
    print(user)