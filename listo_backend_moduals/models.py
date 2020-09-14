from listo_backend_moduals import db, login
from datetime import datetime
from flask_login import UserMixin


@login.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()

class User(db.Model, UserMixin):
    #以下為模型基本資料
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False) #use email as account
    password = db.Column(db.String(80), unique=False, nullable=False)
    username =db.Column(db.String(120), unique=True, nullable=False)

    #以下為串聯其他Table部分
    been_to_ID_list =db.relationship("Map_Address", backref = db.backref("user", lazy =True))##串聯Map_Address表 並用地點名.user反向搜尋
    posts = db.relationship("Post", backref = db.backref("author", lazy =True)) #由Post反向搜尋的時候使用 postName.author

    def __repr__(self):
        #print(self.been_to_ID_list)
        return f'<User {self.username}>'


class Map_Address(db.Model):
    # 以下為模型基本資料
    __tablename__ = "map_address"
    id = db.Column(db.Integer, primary_key=True)
    latitude  = db.Column(db.Float, unique=False, nullable=False)#緯度<float>
    lontitude = db.Column(db.Float, unique=False, nullable=False)#經度<float>


    # 以下為串聯其他Table部分
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False) #串聯User表 外鍵為user.id
    posts = db.relationship("Post", backref=db.backref("place", lazy=True)) #串聯Post表 由Post反向搜尋的時候使用 post.place

    def __repr__(self):
        #print(self.been_here_User_ID)
        return f"<map address {self.id}, {self.latitude}, {self.lontitude} >"

class Post(db.Model):
    # 以下為模型基本資料
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(300), unique=False, nullable=False) #
    timestamp = db.Column(db.DateTime, nullable=False,default=datetime.utcnow)#發文內容 時間戳記

    # 以下為串聯其他Table 外鍵部分
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable =False)
    address_id = db.Column(db.Integer, db.ForeignKey("map_address.id"), nullable=False)

    def __repr__(self):
        return f'<Post {self.content}>'
    

if __name__ == "__main__":
    db.create_all()

    u = User(id=1, email="em", password="123", username="K")
    print(u)
    print(u.posts)
    u.posts.append( Post(content="test") )
    print(u.posts)
    m1 = Map_Address(id =112, latitude =0.5, lontitude=0.4)
    m2 = Map_Address(id=113, latitude=0.6, lontitude=0.4)
    u.been_to_ID_list.append(m1)
    u.been_to_ID_list.append(m2)
    print(m1.user, m2.user)
    print(u.been_to_ID_list)

    