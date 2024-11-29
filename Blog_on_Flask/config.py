import os

app_dir = os.path.abspath(os.path.dirname(__file__))


class BaseConfig:
    image_dir = str(os.path.join(app_dir)) + "/static/upload/"
    DEBUG = True
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a1ceab44fbce8cd4e5c8ca65701b149d3df6b8cc'
    UPLOAD_FOLDER = image_dir
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    POSTS_PER_PAGE = 3


    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(app_dir, 'app.db')




