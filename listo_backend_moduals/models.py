from listo_backend_moduals import db
from datetime import datetime
#from flask_login import UserMixin
from flask import jsonify
import enum
from sqlalchemy import text
from flask_sqlalchemy import orm

db.metadata.clear()

"""@login.user_loader
def load_user(user_id):
    return user.query.filter_by(id=user_id).first()"""


class Privacy_level(enum.Enum):
    open = 0
    close = 1
    private = 2


class Authority(enum.Enum):
    Auth_user = 0
    Normal_user = 1
    Deleted = 2


class tagRelationship(db.Model):
    __tablename__ = "tagRelationship"
    extend_existing = True
    # 以下為模型基本資料
    user_id = db.Column(db.Integer, primary_key=True, nullable=False)
    tag_id = db.Column(db.Integer,  primary_key=True,nullable=False)
    place_id = db.Column(db.Integer, primary_key=True, nullable=False)
    created_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # 發文時間戳記

    def __repr__(self):
        return f'<Tag Relaitonship bewteen user {self.user_id},tag {self.tag_id},place {self.place_id}>'


class user(db.Model):
    __tablename__ = "user"
    extend_existing = True
    __tagEvent = {} #存使用者擁有的tag的tag events

    def getTagEvent(self, tag_id):
        return self.__tagEvent[tag_id]

    def pushTagEvent(self,tag_id, events):
        if self.__tagEvent.get(tag_id):
            self.__tagEvent[tag_id].extend(events)
        else:
            self.__tagEvent[tag_id] = events
        #print(self.tag_event[tag_id])

        # 以下為模型基本資料
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)  # use email as account
    password = db.Column(db.String(500), unique=False, nullable=False)
    username = db.Column(db.String(120), unique=True, nullable=False)
    is_deleted = db.Column(db.Boolean, nullable =False, server_default = text('False'))
    created_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    privacy = db.Column(db.Enum(Authority), unique=False, nullable=False)

    # 以下為串聯其他Table部

    placelist = db.relationship("placeList",
                                      backref=db.backref("author", lazy=True))  #串聯PlaceList表 並用Place名.author反向搜尋
    #article = db.relationship("Article", backref=db.backref("author", lazy=True))  # 由Article反向搜尋的時候使用 post名.author



    def __repr__(self):
        return f'<User {self.username}>'

class tag(db.Model):
    __tablename__ = "tag"

    # 以下為模型基本資料
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), unique=False, nullable=False)  #
    type = db.Column(db.Integer, unique=False, nullable=True)  #
    #privacy = db.Column(db.Enum(Privacy_level), unique=False, nullable=False)
    #is_deleted = db.Column(db.Boolean, nullable =False, server_default = text('False'))


    def __repr__(self):
        return f'<Tag {self.name}, Class {self.type}>'


#先設立關係表，後面當作place跟placelist的中間表

place_relations = db.Table(
    'place_relations',
    db.Column('place_rt', db.Integer, db.ForeignKey('place.id')),
    db.Column('placelist_rt', db.Integer, db.ForeignKey('placeList.id')))


class placeList(db.Model):
    __tablename__ = "placeList"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=False, nullable=False)  # 地點名稱
    description = db.Column(db.String(1000), unique=False, nullable=False)  # 地點敘述
    #privacy = db.Column(db.Enum(Privacy_level), unique=False, nullable=False)
    privacy = db.Column(db.Integer, unique=False, nullable=False)
    user_id =db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)
    coverImageURL = db.Column(db.String(300), unique=False, nullable=True)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # 發文時間戳記
    updated = db.Column(db.DateTime, nullable=True, default=datetime.utcnow,onupdate=datetime.utcnow)  # 更新時間戳記


    place= db.relationship(
        "place", secondary=place_relations, backref="placelists")

    def get_list(self):
        res ={
            "id":self.id,
            "creator_id": self.user_id,
            "name": self.name,
            "coverImageURL": self.coverImageURL,

        }
        return res
    def get_list_info(self):
        res ={
            "creator_username": "",
            "privacy": self.privacy,
            "description": self.description,
            "createdTime": self.createdTime,
            "updatedTime": self.updatedTime

        }
    def __repr__(self):

        return f"<PlaceList {self.id}, {self.name}, description:,{self.description},privacy:, {self.privacy}>"

class place(db.Model):
    __tablename__ = "place"

    # 以下為模型基本資料
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    #以下為地圖資訊 先暫以經緯度代替MAP API的JSON
    latitude = db.Column((db.Numeric(precision=8, asdecimal=False, decimal_return_scale=None)), unique=False, nullable=False)  # 緯度<float>
    longitude = db.Column((db.Numeric(precision=8, asdecimal=False, decimal_return_scale=None)), unique=False, nullable=False)  # 經度<float>
    phone = db.Column(db.String(50), unique=True, nullable=True)
    address = db.Column(db.String(50), unique=True, nullable=True)
    gmap_id = db.Column(db.Integer, unique=True,nullable = True)
    type = db.Column(db.String(50), unique=False, nullable=True)
    system_tag = db.Column(db.String(50), unique=False, nullable=True)

    def location(self):
        map_info = {
            "latitude" : self.latitude,
            "longitude" : self.longitude
        }
        return jsonify(map_info)
    def __repr__(self):
        # print(self.been_here_User_ID)
        return f"<Place {self.id}, {self.latitude}, {self.longitude} >"


class Response(object):
    def __init__(self, data):
        self.status = 1
        self.data = data
        self.msg = ""

    def jsonify_res(self):
        res = {
            "status":self.status,
            "data":self.data,
            "msg":self.msg
        }
        return jsonify(res)

class Mark(db.Model):
    __tablename__ = "Mark"
    gmap_id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Float, unique=False, nullable=False)  # 緯度<float>
    longitude = db.Column(db.Float, unique=False, nullable=False)  # 經度<float>)


    def location(self):
        map_info = {
            "latitude" : self.latitude,
            "longitude" : self.lontitude
        }
        return jsonify(map_info)

if __name__ == "__main__":
    db.drop_all()
    db.create_all()
    #ex = placeList(name= "name", description= "fasf", coverImageURL = "", privacy = "1", places= [1,2], user_id =1)
    #print(ex.place)


