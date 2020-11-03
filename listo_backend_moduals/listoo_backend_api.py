from flask import abort,request
from flask_login import login_user,logout_user, login_required, current_user
from listo_backend_moduals import app, photos_settings
from listo_backend_moduals.models import *
from listo_backend_moduals import bcrypt
import sys
import traceback

def abort_msg(e):
    """500 bad request for exception

    Returns:
        500 and msg which caused problems
    """
    error_class = e.__class__.__name__ # 引發錯誤的 class
    detail = e.args[0] # 得到詳細的訊息
    cl, exc, tb = sys.exc_info() # 得到錯誤的完整資訊 Call Stack
    lastCallStack = traceback.extract_tb(tb)[-1] # 取得最後一行的錯誤訊息
    fileName = lastCallStack[0] # 錯誤的檔案位置名稱
    lineNum = lastCallStack[1] # 錯誤行數
    funcName = lastCallStack[2] # function 名稱
    # generate the error message
    errMsg = "Exception raise in file: {}, line {}, in {}: [{}] {}. Please contact the member who is the person in charge of project!".format(fileName, lineNum, funcName, error_class, detail)
    # return 500 code
    abort(500, errMsg)

# ======================================================
# Common
# ======================================================

@app.route("/common/get_recommend_lists/", methods=['GET', 'POST'])
def GetRecommandLists():
    try:
        item = placeList.query.filter_by(id=1).first() #暫以第一個取代
        cur_place = []  # 找到place
        for p in item.place:
            cur_place.append({
                "id": p.id,
                "name": p.name,
                "latitude": p.latitude,
                "longitude": p.longitude,
                "phone": p.phone,
                "address": p.address,
                "gmap_id": p.gmap_id,
                "type": p.type
            })
        Rec_lists = [{
                "id":item.id,
                "name":item.name,
                "description":item.description,
                "place":cur_place,
                "privacy" : item.privacy,
                "user_id":item.user_id,
                "coverImageURL" : item.coverImageURL,
                "created" : item.created,
                "update" : item.update
            }]

        respond = Response(data={"lists" : Rec_lists})  # 建立回應實例 (實例內容見model內的Response class)

        if len(Rec_lists)==0:
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
        rec_tag_list=[]
        for item in  cur_tag.items:
           rec_tag_list.append({
               "id": item.id,
               "name": item.name,
               "type": item.type
           })
        res = Response(data={"tags" : rec_tag_list})  # 建立回應實例 (實例內容見model內的Response class)
        if len(rec_tag_list)==0:
            res.status = 0
            res.msg = "No hot tag was found"
        return res.jsonify_res()
    except Exception as e:
        abort_msg(e)

@app.route("/common/get_list/", methods=["GET",'POST'])
def GetList():
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
        respond_tags =[]
        if list_id:
            cur_list = placeList.query.filter_by(id=list_id).first()
            if cur_list:
                for item in cur_list.place:
                    respond_places.append({
                    "id":item.id,
                    "name" :item.name,
                    "latitude" :item.latitude,
                    "longitude" :item.longitude,
                    "phone": item.phone,
                    "address" : item.address,
                    "gmap_id" : item.gmap_id,
                    "type" :item.type
                    })
        if tag_id:
            for t in tag_id:
                cur_tag = tag.query.filter_by(id= t).first()
                if cur_tag:
                    respond_tags.append({
                        "id": cur_tag.id,
                        "name": cur_tag.name,
                        "type": cur_tag.type
                    })


        respond = Response(data=
                       {"tags": respond_tags,
                        "places": respond_places,
                        "list_id": cur_list.id,
                        "list_name": cur_list.name
                        })

        if not cur_list:
            respond.status = 0
            respond.msg = "No list was found"
        return respond.jsonify_res()
    except Exception as e:
        abort_msg(e)

@app.route("/common/search_tags/", methods=['GET', 'POST'])
def SearchTags():
    try:
        data = request.get_json()
        text = data["text"]

        cur_tag = tag.query.filter(tag.name.like("%{}%".format(text))).all()
        respond_tags =[]
        for item in cur_tag:
            respond_tags.append({
                "id": item.id,
                "name": item.name,
                "type": item.type
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
def Auth():
    try:
        data = request.get_json()
        email = data["email"]
        name = data["username"]
        psw = data["password"]
        password = bcrypt.generate_password_hash(psw).decode('utf-8')
        respond = Response(data = {"email": email,
                                   "name":name,
                                   "password":password})
        def validate_username(respond):
            User = user.query.filter_by(username = respond.data["name"]).first()
            if User:
                respond.status =0
                respond.msg ="Username was taken"
                return False
            return True
        def validate_email(respond):
            email = user.query.filter_by(email = respond.data["password"]).first()
            if email:
                respond.status =0
                respond.msg ="Email was taken"
                return False
            return True

        if validate_email(respond) and validate_username(respond):
            User = user(username=name, password=password, email=email, privacy = Authority.Normal_user)
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
            respond.msg = "Logged in"
            respond.data = {"user_id": User.id}
            login_user(User)
        else:
            respond.msg = "Not valid"
            respond.status =0
        return respond.jsonify_res()
    except Exception as e:
        abort_msg(e)

@app.route('/auth/logout/', methods=['GET'])
def Logout():
    try:
        respond = Response(data={"username": current_user.username})
        respond.msg ="User logged out"
        logout_user()
        return respond.jsonify_res()
    except Exception as e:
        abort_msg(e)

  #======================================================
  # User
  #======================================================

@app.route("/user/get_user_lists/", methods=["GET",'POST'])
@login_required
def GetUserLists():
    try:
        data = request.get_json()
        filter_ = data["filter"]
        respond_tags =[] #最後要回傳的tags
        #user_lists = [] #最後要回傳的list
        tag_in_place_dict = {} #place有含filter中tag的dict 用tagid當key 內容為有該tag的place


        for item in current_user.placelist:
            temp_tags = {}  # 紀錄list的所有tag
            cur_place = item.place #該placelist下的place
            for p in cur_place:
                cur_rels = tagRelationship.query.filter_by(place_id = p.id, user_id=current_user.id).all() #用登入的userid 跟placeid 找關係再列出所有的tag
                for rel in cur_rels:
                    if not temp_tags.get(item.id): #用dict 紀錄user自己的placelist下面包含的place所有的tag key 為placelistid
                        temp_tags[item.id] = [rel.tag_id]
                    else:
                        temp_tags[item.id].append(rel.tag_id)

                    #處理有該tag 的place

                    if not tag_in_place_dict.get(rel.tag_id):
                        tag_in_place_dict[rel.tag_id] = {}
                    if rel.tag_id in filter_ and not tag_in_place_dict[rel.tag_id].get(p.id): #如果tag 在filter裡 且place不在 該tag裡面
                        tag_in_place_dict[rel.tag_id][p.id] = {
                                            "id":p.id,
                                            "name" :p.name,
                                            "latitude" :p.latitude,
                                            "longitude" :p.longitude,
                                            "phone": p.phone,
                                            "address" : p.address,
                                            "gmap_id" : p.gmap_id,
                                            "type" :p.type
                        }


            if len(temp_tags.keys())>0:
                respond_tags.append(temp_tags)
        """for cur_id in tag_in_place_dict.keys():
            item = placeList.query.filter_by(id = cur_id).first()
            user_lists.append({
                "id": item.id,
                "name": item.name,
                "description": item.description,
                "place": item.place,
                "privacy": item.privacy,
                "user_id": item.user_id,
                "coverImageURL": item.coverImageURL,
                "created": item.created,
                "update": item.update,
                "tags":temp_tags[cur_id]
            })"""


        respond = Response(data=
                       {"lists": tag_in_place_dict,
                        "tags": respond_tags})

        if not len(tag_in_place_dict.keys()) or not len(respond_tags):
            respond.status = 0

            if not len(tag_in_place_dict.keys()):
                respond.msg += "No list was found"
            if not len(respond_tags):
                respond.msg += " No Tag was found"
        return respond.jsonify_res()
    except Exception as e:
        abort_msg(e)


@app.route("/user/create_list/", methods=["GET",'POST'])
@login_required
def CreateList():
    try:
        data = request.get_json()
        name = data["name"]
        description = data["description"]
        coverImageURL = data['coverImageURL']
        privacy = data['privacy']
        places = data['places']
        new_list = placeList(name= name, description= description, coverImageURL= coverImageURL, privacy = privacy,  user_id =current_user.id)
        for p in places:
            place_query = place.query.filter_by(id = p).first()
            if place_query:
                new_list.place.append(place_query)
        db.session.add(new_list)
        db.session.commit()
        respond_places = {}
        for p in new_list.place:
            respond_places[p.id] = {
                "id": p.id,
                "name": p.name,
                "latitude": p.latitude,
                "longitude": p.longitude,
                "phone": p.phone,
                "address": p.address,
                "gmap_id": p.gmap_id,
                "type": p.type
            }


        respond = Response(data=
                       {"list_id": new_list.id,
                        "places": respond_places})
        return respond.jsonify_res()
    except Exception as e:
        abort_msg(e)

@app.route("/user/add_list_places/", methods=["GET",'POST'])
@login_required
def AddListPlaces():
    try:
        data = request.get_json()
        list_id = data["list_id"]
        places = data['places']

        respond = Response(data ={"list_id":list_id,
                                "place_added":[]})

        list_query = placeList.query.filter_by(id=list_id).first()
        for i in list_query.place:
            print(i.id)
        for p_id in places:
            place_query = place.query.filter_by(id=p_id).first()
            if place_query:
                list_query.place.append(place_query)
                respond.data["place_added"].append(place_query.id)
                db.session.commit()
        if not len(respond.data["place_added"]) or not list_id:
            respond.status = 0
            respond.msg = "No place or list was found"
        return respond.jsonify_res()

    except Exception as e:
        abort_msg(e)


@app.route("/user/remove_list_places/", methods=["GET",'POST'])
@login_required
def RemoveListPlaces():
    try:
        data = request.get_json()
        list_id = data["list_id"]
        places = data['places']

        respond = Response(data={"list_id": list_id,
                                 "place_removed": []})

        list_query = placeList.query.filter_by(id=list_id).first()
        #用while實作 以後處理

        """
        idx = 0
        for i  in range(places): #要移除的place
            p_id = places[i]
            cur_list_len = len(list_query.place)       
            
            while counter!=cur_list_len:
                
            for p in list_query.place: #清單原本的place
                if p.id == p_id: 
                    list_query.place.remove(p)
                    respond.data["place_removed"].append(p_id)"""

        #用雙迴圈是因為移除地點後 generator給的list不同 所以要重新跑一次
        for p_id in places: #要移除的place
            for p in list_query.place: #清單原本的place
                if p.id == p_id:
                    list_query.place.remove(p)
                    respond.data["place_removed"].append(p_id)

        db.session.commit()
        if not len(respond.data["place_removed"]) or not list_id:
            respond.status = 0
            respond.msg = "No place or list was found"
        return respond.jsonify_res()

    except Exception as e:
        abort_msg(e)

@app.route("/user/edit_list/", methods=["GET",'POST'])
@login_required
def EditList():
    try:
        data = request.get_json()
        cur_list = data["list_id"]
        edit_name = data["name"]
        edit_description = data["description"]
        edit_privacy = data["privacy"]
        edit_coverImageURL = data['coverImageURL']

        cur_list = placeList.query.filter_by(id = cur_list).first()
        if edit_name:
            cur_list.name = edit_name
        if edit_description:
            cur_list.description = edit_description
        if edit_coverImageURL:
            cur_list.coverImageURL = edit_coverImageURL
        if edit_privacy:
            cur_list.privacy = edit_privacy

        respond = Response(data={
            "name":cur_list.name,
            "edited_name" : cur_list.description,
            "edited_privacy" : cur_list.privacy,
            "edited_coverImageURL" : cur_list.coverImageURL
        })
        respond.msg = "Edited successfully"
        return respond.jsonify_res()
    except Exception as e:
        abort_msg(e)


@app.route("/user/modify_place_tag/", methods=["GET",'POST'])
@login_required
def ModifyPlaceTag():
    try:
        import random
        import string
        def get_random_string(length):
            letters = string.ascii_lowercase
            result_str = ''.join(random.choice(letters) for i in range(length))
            return result_str
        data = request.get_json()
        gmap_id = data["gmap_id"]
        add_tags = data["add"]
        remove_tags = data["remove"]
        new_tags = data["newTags"]


        gmap_mark = Mark.query.filter_by(gmap_id = gmap_id).first()
        if not gmap_mark:
            gmap_mark = Mark(latitude =random.uniform(-100, 100),longitude = random.uniform(-100, 100)) #因為還沒接google API 先暫時建一個值為零
            db.session.add(gmap_mark)
            db.session.commit()

        cur_plcae = place.query.filter_by(gmap_id=gmap_mark.gmap_id).first()
        if not cur_plcae:
            #這邊要先接google API 回傳地點資訊後再新建 暫時以0代替
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

        for t in add_tags: #place新增原有的tag
            if not tagRelationship.query.filter_by(user_id = current_user.id, tag_id =t, place_id=cur_plcae.id).first():
                newTR = tagRelationship(user_id = current_user.id, tag_id =t, place_id=cur_plcae.id)
                db.session.add(newTR)
                db.session.commit()
        for t in remove_tags:#placeg刪除原有的tag
            tagRelationship.query.filter_by(user_id = current_user.id,tag_id = t, place_id=cur_plcae.id).delete()
            db.session.commit()

        respond_new_tags =[]
        for item  in new_tags:
            newTag = tag(name = item['name'], type= item['type']) #新增tag
            db.session.add(newTag)
            db.session.commit()
            tag_relationship = tagRelationship(place_id=cur_plcae.id, user_id=current_user.id, tag_id = newTag.id) #新增place tag user關聯
            db.session.add(tag_relationship)
            db.session.commit()
            respond_new_tags.append(newTag.id)

        #回傳被修改的place, newTag, mark
        respond = Response(data = {
            "modified_place_id":cur_plcae.id,
            "newTag" : respond_new_tags,
            "mark_id": gmap_mark.gmap_id,
            "mark_longitude":gmap_mark.latitude,
            "mark_latitude":gmap_mark.latitude
        })
        return respond.jsonify_res()
    except Exception as e:
        abort_msg(e)

# ======================================================
# Map
# ======================================================

@app.route("/map/get_marks/", methods=["GET",'POST'])
@login_required
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
        respond = Response(data = {
            "Marks":respond_mark_list #回傳gmap_id的array
        })
        return respond.jsonify_res()
    except Exception as e:
        abort_msg(e)

@app.route("/map/get_place_info/", methods=["GET",'POST'])
@login_required
def GetPlaceInfo():
    try:
        data = request.get_json()
        gmap_id = data['gmap_id']
        cur_place = place.query.filter_by(gmap_id= gmap_id).first()
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
@login_required
def GetPlaceTag():
    try:
        data = request.get_json()
        place_id = data["gmap_id"]
        cur_user_tags = tagRelationship.query.filter_by(user_id= current_user.id, place_id = place_id).all() #用currentuser.id跟place_id找 relationship
        tags = {} #回應的tag_list
        for item in cur_user_tags:
            cur_tagid = item.tag_id
            cur_tag = tag.query.filter_by(id = cur_tagid).first() #反找到的tagid
            if cur_tag and not tags.get(cur_tag.id):
                tags[cur_tag.id] = ({"tag_id":cur_tag.id,
                                 "tag_name":cur_tag.name,
                                 "tag_type": cur_tag.type
                                 })
        respond = Response(data = {
            "tags":tags
        })
        return respond.jsonify_res()
    except Exception as e:
        abort_msg(e)

@app.route("/map/search_tag/", methods=["GET", 'POST'])
@login_required
def SearchTag():
    try:
        data = request.get_json()
        place_id = data["place_id"] #place_id
        type = data["type"] #place type
        text = data["text"] #搜尋的關鍵字


        tags = {} #要回傳的tags

        if place_id:

            cur_tag_rel = tagRelationship.query.filter_by(user_id =current_user.id, place_id = place_id).all()
            for row in cur_tag_rel:
                cur_tag_id = row.tag_id
                cur_tag = tag.query.filter_by(id = cur_tag_id).first()
                #print(cur_tag)
                if cur_tag and not tags.get(cur_tag.id):
                    tags[cur_tag.id] = {"tag_id":cur_tag.id,
                                 "tag_name":cur_tag.name,
                                 "tag_type": cur_tag.type
                                 }
        if len(type):
            cur_place_type = place.query.filter_by(type=type).all()
            for p in cur_place_type:
                tag_query = tagRelationship.query.filter_by(place_id=p.id).all()
                for t in tag_query:
                    item = tag.query.filter_by(id=t.tag_id).first()
                    if item and not tags.get(item.id):
                        tags[item.id] = {"tag_id":item.id,
                                     "tag_name":item.name,
                                     "tag_type": item.type
                                     }
        if len(text):
            cur_tags_text = tag.query.filter(tag.name.like("%{}%".format(text))).all()
            if len(cur_tags_text):
                for item in cur_tags_text:
                    if item and not tags.get(item.id):
                        tags[item.id] = {"tag_id":item.id,
                                     "tag_name":item.name,
                                     "tag_type": item.type
                                     }
        respond = Response(data = {
            "tags":tags
        })
        if not len(tags):
            respond.msg = "No tag was found"
            respond.status =0
        return respond.jsonify_res()
    except Exception as e:
        abort_msg(e)

@app.route("/map/candidate_tag/", methods=["GET", 'POST'])
@login_required
def CandidateTag():
    try:
        data = request.get_json()
        gmap_id = data["gmap_id"] #要搜尋的place gmap_id
        type_ = data["type"] #place type
        tags = {} #回應的tag_list
        limit_num = data["limit"] #限制的筆數
        gmapid_places = place.query.filter_by(gmap_id = gmap_id).limit(limit_num//2).all() #用gmap_id搜尋的tagRelationship
        type_place = place.query.filter_by(type = type_).limit(limit_num//2).all() #用type搜尋的place

        for item in gmapid_places:
            tag_query = tagRelationship.query.filter_by(place_id =item.id).all() #用place 反找tagRelationship再找tagid
            for row in tag_query:
                if not tags.get(row.tag_id):
                    t = tag.query.filter_by(id = row.tag_id).first() #反找找到的tag
                    tags[row.tag_id] = ({"tag_id":t.id,
                                     "tag_name":t.name,
                                     "tag_type": t.type
                                     })
        for p in type_place:
            cur_tag_relation = tagRelationship.query.filter_by(place_id = p.id).all() #用type找place再找tag
            for rel in cur_tag_relation:
                item = tag.query.filter_by(id = rel.tag_id).first()
                if item and not tags.get(item.id):
                    tags[item.id] ={"tag_id":item.id,
                                     "tag_name":item.name,
                                     "tag_type": item.type
                                     }
        respond = Response(data = {
            "tags":tags
        })
        return respond.jsonify_res()
    except Exception as e:
        abort_msg(e)






if __name__ == "__main__":
    user = user.query.filter_by(username = 1).first()
    print(user)