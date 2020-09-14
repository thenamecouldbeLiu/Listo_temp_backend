import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    #上傳KEY
    SECRET_KEY = os.environ.get('SECRET_KEY') or "LONG_LONG_KEY_HERE" #Flask需要的後台金鑰
    #RECAPTCHA_PUBLIC_KEY = os.environ.get('RECAPTCHA_PUBLIC_KEY') or "LONG_LONG_PUBLIC_KEY_HERE" #RECAPTCHA金鑰
    #RECAPTCHA_PRIVATE_KEY = os.environ.get('RECAPTCHA_PRIVATE_KEY') or "LONG_LONG_PRIVATE_KEY_HERE"
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://listo_admin:msk60514@localhost:3306/Listo_local' or 'sqlite:///' + os.path.join(basedir, 'app.db')
    #資料庫連結

    SQLALCHEMY_TRACK_MODIFICATIONS = False