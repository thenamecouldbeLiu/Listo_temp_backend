from flask import Flask
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_bootstrap import Bootstrap
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from listo_backend_moduals.config import Config


app = Flask(__name__) #initialize
bootstrap = Bootstrap(app) #Flask_bootstrap布置表格
#csrf = CSRFProtect(app) #做CSRF保護
bcrypt = Bcrypt(app) #加密密碼輸送(HASH)
db = SQLAlchemy(app) #連接database
print("db connected")
app.config.from_object(Config) #讀取config

#以下為Login功能初始化
login = LoginManager(app)
login.login_view = "login"
login.login_message = "登入後才能訪問"
login.login_message_category = "info"

#以下為圖片上傳功能初始化
photos_settings = UploadSet('photos', IMAGES) #限制上傳僅能為照片檔 (詳細副檔名見config)
configure_uploads(app, photos_settings) #將上傳功能跟app綁定
patch_request_class(app)  # set maximum file size, default is 16MB

#import 路徑給APP
import listo_backend_moduals.listoo_backend_api



