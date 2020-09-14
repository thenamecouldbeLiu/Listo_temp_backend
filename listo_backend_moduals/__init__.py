from flask import Flask,flash, render_template, url_for, redirect, flash, request, jsonify
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_bootstrap import  Bootstrap
from listo_backend_moduals.config import Config


app = Flask(__name__) #initialize
bootstrap = Bootstrap(app)
csrf = CSRFProtect(app) #做CSRF保護
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
app.config.from_object(Config)
login = LoginManager(app)
login.login_view = "login"
login.login_message = "登入後才能訪問"
login.login_message_category = "info"

import listo_backend_moduals.routes



