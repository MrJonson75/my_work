import os
import re
from datetime import datetime, timezone, date


from flask import render_template, flash, redirect, url_for, request, abort, current_app
from urllib.parse import urlsplit

from slugify import slugify
from werkzeug.utils import secure_filename

from app import app
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
from app import db
from app.models import Category, Post, User, Comment
from app.forms import (LoginForm, RegistrationForm, EditProfileForm, EmptyForm,
                       ArticleForm, ArticleFormUpdate, CommentForm)

menu = [
    {"title": "Главная", "url": "/"},
    {"title": "О нас", "url": "/about"},
    {"title": "Добавить статью", "url": "/add_article"},
    {"title": "Мои статьи", "url": "/explore"},
    {"title": "Авторизация", "url": "/login"}

]


# ---------------------------------------Утилиты-----------------------------------
def file_path(s: str):
    sl = s.rfind("/")
    f_path = s[0:sl + 1]
    f_name = s[sl + 1:len(s)]
    return f_name, f_path


@app.before_request
def before_request():
    """
     Сохраняет текущее время в last_seen поле для данного
     пользователя всякий раз, когда этот
     пользователь отправляет запрос на сервер.
    :return:
    """
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()


# ------------------------------------------------------------------------------------------------------

@app.route('/')
@app.route('/index')
def index():
    """
    Возвращает все статьи
    :return:
    """

    b_menu = db.session.query(Category).all()

    page = request.args.get('page', 1, type=int)
    query = sa.select(Post).order_by(Post.timestamp.desc())
    posts = db.paginate(query, page=page,
                        per_page=app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) \
        if posts.has_prev else None

    return render_template('index.html', article=posts,
                           title="Статьи о компьютерных играх", menu=menu, b_menu=b_menu,
                           posts=posts.items, next_url=next_url, prev_url=prev_url)


@app.route('/<id>')
def cat_sort(id):
    queue = sa.select(Post).where(Post.cat_id == id)
    result = db.session.scalars(queue).all()
    b_menu = db.session.query(Category).all()
    return render_template('index.html', article=result,
                           title="Статьи о компьютерных играх", menu=menu, b_menu=b_menu)


# http://localhost/open/<slug>> открыть статью
@app.route('/open/<string:slug>', methods=['GET', 'POST'])
@login_required
def show_article(slug):
    posts = db.session.scalar(sa.select(Post).where(Post.slug == slug))
    query = sa.select(Comment).where(Comment.post_id == posts.id)
    comment = db.session.scalars(query).all()

    form = CommentForm()
    if form.validate_on_submit():
        com = Comment(
            body=form.body.data,
            authors=current_user,
            post_id=posts.id
        )
        db.session.add(com)
        db.session.commit()
        flash('Ваш комментарий теперь в прямом эфире!')
        # return redirect(url_for('index'))
        return redirect(url_for("show_article", slug=posts.slug))

    return render_template('article.html', article=posts, form=form,
                           title=posts.title, comment=comment, menu=menu, b_menu=Category.query.all())


@app.route('/explore')
@login_required
def explore():
    """
    Возвращает статьи пользователя
    Метод following_posts класса User возвращает объект запроса SQLAlchemy,
    который настроен для получения записей, которые интересуют пользователя,
    из базы данных. После выполнения этого запроса и вызова all() для объекта
    результатов переменная posts определяется списком со всеми результатами.
    :return:
    """
    # posts = db.session.scalars(current_user.following_posts()).all()
    user = db.first_or_404(sa.select(User).where(User.username == current_user.username))
    page = request.args.get('page', 1, type=int)
    query = user.users.select().order_by(Post.timestamp.desc())
    posts = db.paginate(query, page=page,
                        per_page=app.config['POSTS_PER_PAGE'],
                        error_out=False)
    next_url = url_for('user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None

    return render_template('index.html', article=posts,
                           title="Статьи о компьютерных играх", menu=menu, b_menu=Category.query.all(),
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)


@app.route('/about')
def about():
    return render_template('about.html',
                           title="Немного о сайте", menu=menu, b_menu=Category.query.all())


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Неверное имя пользователя или пароль')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
            return redirect(next_page)
        return redirect(url_for('index'))
    return render_template('login.html',
                           title='Авторизация', form=form, menu=menu, b_menu=Category.query.all())


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Поздравляем, теперь вы зарегистрированный пользователь!')
        return redirect(url_for('login'))

    return render_template('register.html',
                           title='Регистрация пользователя', form=form, menu=menu, b_menu=Category.query.all())


@app.route('/user/<username>')
@login_required
def user(username):

    user = db.first_or_404(sa.select(User).where(User.username == username))
    page = request.args.get('page', 1, type=int)
    query = user.users.select().order_by(Post.timestamp.desc())
    posts = db.paginate(query, page=page,
                        per_page=app.config['POSTS_PER_PAGE'],
                        error_out=False)
    next_url = url_for('user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    form = EmptyForm()
    return render_template('profile.html', title="Личная територия",
                           user=user, posts=posts, form=form, menu=menu,
                           next_url=next_url, prev_url=prev_url, b_menu=Category.query.all())


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Ваши изменения сохранены.')
        return redirect(url_for('user', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me

    return render_template('edit_profile.html',
                           title='Редактирование профиля', form=form, menu=menu, b_menu=Category.query.all())


@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    """
    Вбюха подписки
    :param username:
    :return:
    """
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == username))
        if user is None:
            flash(f'User {username} not found.')
            return redirect(url_for('index'))
        if user == current_user:
            flash('Вы не можете следовать за собой!')
            return redirect(url_for('user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash(f'Вы следуете {username}!')
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))


@app.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    """
    Вьюха маршрута отмены подписки
    :param username:
    :return:
    """
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == username))
        if user is None:
            flash(f'User {username} not found.')
            return redirect(url_for('index'))
        if user == current_user:
            flash('Вы не можете отписаться!')
            return redirect(url_for('user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash(f'Вы не следуете {username}.')
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))


@app.route('/add_article', methods=['GET', 'POST'])
@login_required
def add_article():
    """
    Добавляет статью в базу данных
    :return:
    """
    groups = Category.query.all()
    form = ArticleForm()
    form.cat_id.choices = [(i.id, i.cat) for i in groups]
    if form.validate_on_submit():
        file1 = form.foto_title.data
        file2 = form.foto_body.data
        filename_title = secure_filename(form.foto_title.data.filename)
        filename_body = secure_filename(form.foto_body.data.filename)
        data = str(date.today())
        patch = str(os.path.join(app.static_folder + "/upload/image_article/" + data))
        if not os.path.exists(patch):
            os.makedirs(patch)
        file1.save(os.path.join(app.static_folder + "/upload/image_article/" + data, filename_title))
        file2.save(os.path.join(app.static_folder + "/upload/image_article/" + data, filename_body))
        image_url_title = "/upload/image_article/" + data + "/" + filename_title
        image_url_body = "/upload/image_article/" + data + "/" + filename_body

        post = Post(
            title=form.title.data,
            description=form.description.data,
            article=form.article.data,
            author=current_user,
            slug=slugify(str(form.title.data)),
            cat_id=form.cat_id.data,
            foto_title=image_url_title,
            foto_body=image_url_body
        )
        db.session.add(post)
        db.session.commit()
        flash('Ваша статья теперь в прямом эфире!')
        return redirect(url_for('index'))
    # form = ArticleForm()
    return render_template("add_article.html",
                           title='Добавить статью', form=form, menu=menu, b_menu=Category.query.all())


@app.route('/post/<string:slug>/delete', methods=['POST', 'GET'])
@login_required
def delete_post(slug):
    objects = sa.select(Post).where(Post.slug == slug)
    posts = db.session.scalar(objects)
    if posts.author != current_user:
        abort(403)
    try:
        os.unlink(os.path.join(current_app.root_path, f'static{posts.foto_title}'))
        os.unlink(os.path.join(current_app.root_path, f'static{posts.foto_body}'))
        db.session.delete(posts)
    except:
        db.session.delete(posts)
    db.session.commit()
    flash('Данный пост был удален', 'success')
    return redirect(url_for('index'))


@app.route('/post/<string:slug>/update', methods=['GET', 'POST'])
@login_required
def update_post(slug):
    objects = sa.select(Post).where(Post.slug == slug)
    posts = db.session.scalar(objects)
    groups = Category.query.all()

    # Проверяем, что текущий пользователь является автором
    if posts.author != current_user:
        flash('Нет доступа к обновлению статьи!', 'danger')
        return redirect(url_for('index'))

    form = ArticleFormUpdate()
    form.cat_id.choices = [(i.id, i.cat) for i in groups]

    if request.method == 'GET':
        # Заполняем форму текущими значениями поста
        form.title.data = posts.title
        form.description.data = posts.description
        form.article.data = posts.article
        form.cat_id.data = posts.cat_id  # Заполняем категорию

    # Проверяем, была ли отправлена форма
    if form.validate_on_submit():
        # Обновляем заголовок
        if form.foto_title.data:
            # Если загружается новое изображение, удаляем старое
            if posts.foto_title and os.path.exists(
                    os.path.join(current_app.root_path, f'static{posts.foto_title}')):
                os.unlink(os.path.join(current_app.root_path, f'static{posts.foto_title}'))
            file1 = form.foto_title.data
            filename_title = secure_filename(file1.filename)
            data = str(date.today())
            patch = os.path.join(app.static_folder, "upload/image_article", data)
            if not os.path.exists(patch):
                os.makedirs(patch)
            file1.save(os.path.join(patch, filename_title))
            posts.foto_title = f"/upload/image_article/{data}/{filename_title}"
        # Если новое изображение не загружено, оставляем старое значение
        else:
            posts.foto_title = posts.foto_title  # Сохраняем старое значение

        # Аналогично для фото тела статьи
        if form.foto_body.data:
            if posts.foto_body and os.path.exists(os.path.join(current_app.root_path, f'static{posts.foto_body}')):
                os.unlink(os.path.join(current_app.root_path, f'static{posts.foto_body}'))
            file2 = form.foto_body.data
            filename_body = secure_filename(file2.filename)
            data = str(date.today())
            patch = os.path.join(app.static_folder, "upload/image_article", data)
            if not os.path.exists(patch):
                os.makedirs(patch)
            file2.save(os.path.join(patch, filename_body))
            posts.foto_body = f"/upload/image_article/{data}/{filename_body}"
        else:
            posts.foto_body = posts.foto_body  # Сохраняем старое значение

        # Обновляем остальные поля
        posts.title = form.title.data
        posts.description = form.description.data
        posts.article = form.article.data
        posts.slug = slugify(str(form.title.data))
        posts.cat_id = form.cat_id.data

        # Сохраняем изменения в базе данных

        db.session.commit()
        flash(f'Ваша статья: {form.title.data} успешно обновлена')
        return redirect(url_for('index'))

    return render_template("edit_article.html",
                           title=f'Редактировать статью: {posts.article}', posts=posts, form=form, menu=menu,
                           b_menu=groups)
