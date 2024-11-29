from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, FileField
from wtforms.fields.simple import TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length, InputRequired, Optional
import sqlalchemy as sa

from app import db
from app.models import User, Post, Category


class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=4, max=100,
                                                                          message="Пароль должен быть от 4 до 100 символов")])
    remember_me = BooleanField("Запомнить", default=False)
    submit = SubmitField("Войти")


class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email("Некорректный email")])
    password = PasswordField('Пароль',
                             validators=[DataRequired(), Length(min=4, max=100,
                                                                message="Пароль должен быть от 4 до 100 символов")])

    password2 = PasswordField('Повторите пароль',
                              validators=[DataRequired(), EqualTo('password', message="Пароли не совпадают")])

    submit = SubmitField('Регистрация')

    def validate_username(self, username):
        user = db.session.scalar(sa.select(User).where(User.username == username.data))
        if user is not None:
            raise ValidationError('Используйте другое имя пользователя.')

    def validate_email(self, email):
        user = db.session.scalar(sa.select(User).where(User.email == email.data))
        if user is not None:
            raise ValidationError('Используйте другой адрес электронной почты.')


class EditProfileForm(FlaskForm):
    username = StringField('Пользователь', validators=[DataRequired()])
    about_me = TextAreaField('Немного обо мне', validators=[Length(min=0, max=140)])
    submit = SubmitField('Отправить')

    def __init__(self, original_username, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = db.session.scalar(sa.select(User).where(
                User.username == self.username.data))
            if user is not None:
                raise ValidationError('Используйте другое имя пользователя.')


class EmptyForm(FlaskForm):
    submit = SubmitField('Нажать')


class ArticleForm(FlaskForm):
    title = StringField('Название статьи', validators=[DataRequired(), Length(min=1, max=250)])
    description = TextAreaField('Краткое описание', validators=[DataRequired(), Length(min=1, max=500)])
    article = TextAreaField('Статья (можно использовать HTML)', validators=[DataRequired()])
    cat_id = SelectField("Выберете категорию", coerce=int)
    foto_title = FileField("Загрузить фото для заголовка", validators=[FileRequired()])
    foto_body = FileField("Загрузить фото для статьи", validators=[FileRequired()])

    submit = SubmitField('Отправить')


class ArticleFormUpdate(FlaskForm):
    title = StringField('Название статьи', validators=[DataRequired(), Length(min=1, max=250)])
    description = TextAreaField('Краткое описание', validators=[DataRequired(), Length(min=1, max=500)])
    article = TextAreaField('Статья (можно использовать HTML)', validators=[DataRequired()])
    cat_id = SelectField("Выберете категорию", coerce=int)
    foto_title = FileField("Загрузить фото для заголовка", validators=[Optional()])
    foto_body = FileField("Загрузить фото для статьи", validators=[Optional()])

    submit = SubmitField('Отправить')


# def edit_post(request, id):
#     post = Post.query.get(id)
#     form = ArticleForm(request.POST, obj=post)
#     form.cat_id.choices = [(g.id, g.cat) for g in Category.query.order_by('cat')]


class CommentForm(FlaskForm):
    body = TextAreaField('Ваш комментарий', validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Опубликовать')
