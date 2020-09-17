import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    #上傳KEY
    SECRET_KEY = os.environ.get('SECRET_KEY') or "LONG_LONG_KEY_HERE" #Flask需要的後台金鑰
    #RECAPTCHA_PUBLIC_KEY = os.environ.get('RECAPTCHA_PUBLIC_KEY') or "LONG_LONG_PUBLIC_KEY_HERE" #RECAPTCHA金鑰
    #RECAPTCHA_PRIVATE_KEY = os.environ.get('RECAPTCHA_PRIVATE_KEY') or "LONG_LONG_PRIVATE_KEY_HERE"
    SQLALCHEMY_DATABASE_URI = 'postgres://xbddmsvnzegmoq:1e4bec4890270d06f18a1476e895541f09a0c6fbae1aeebeef19cbbf21642b43@ec2-3-216-92-193.compute-1.amazonaws.com:5432/depvg6qvmg6mf9' 
    #資料庫連結
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'} #允許的上傳圖檔
    UPLOADED_PHOTOS_DEST = "D:\Storage Test"