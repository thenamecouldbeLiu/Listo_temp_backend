from flask_wtf import FlaskForm, RecaptchaField
from flask_wtf.file import FileField,  FileAllowed
from wtforms import StringField,  SubmitField, BooleanField, PasswordField, TextAreaField, FloatField
from wtforms.validators import DataRequired, Length, NumberRange, Email, EqualTo, ValidationError
from listo_backend_moduals import photos_settings
from listo_backend_moduals.models import User, Map_Address




class RegisterForm(FlaskForm):
    username = StringField("用戶名", validators=[DataRequired(),Length(min = 6 ,max =20
                                                                    )])
    password = PasswordField("密碼", validators=[DataRequired(), Length(min = 8)])
    repeatpsw = PasswordField("重複密碼", validators=[DataRequired(), EqualTo("password")])
    email = StringField("信箱", validators=[DataRequired(), Email()])
    #recaptcha = RecaptchaField()
    submit = SubmitField("註冊")

    def validate_username(self, username):
        user = User.query.filter_by(username = username.data).first()
        if user:
            raise ValidationError("此用戶已被註冊")
    def validate_email(self, user_email):
        email = User.query.filter_by(email = user_email.data).first()

        if email:
            print(user_email)
            raise ValidationError("此信箱已被註冊")


class LoginForm(FlaskForm):
    email = StringField("信箱", validators=[DataRequired(), Email()]) #用信箱當帳號登入
    password = PasswordField("密碼", validators=[DataRequired(), Length(min = 8)])
    remember = BooleanField("保存登入資訊")
    submit = SubmitField("登入")


class PostForm(FlaskForm):
    latitude = FloatField(validators=[DataRequired()])
    lontitude = FloatField(validators=[DataRequired()])
    tag = StringField(validators=[DataRequired()])
    tag_class = StringField(validators=[DataRequired()])
    text = TextAreaField("感覺如何", validators=[DataRequired(), Length(max=300)])
    image = FileField("上傳照片", validators=[FileAllowed(photos_settings, 'IMAGE ONLY')])

    submit = SubmitField("發文")