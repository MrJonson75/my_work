from flask import Flask
from config import BaseConfig
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager


app = Flask(__name__)
app.config.from_object(BaseConfig)
app.config['MAX_CONTENT_LENGTH'] = 1000 * 1000
app.config['UPLOAD_FOLDER'] = BaseConfig.UPLOAD_FOLDER
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'

from app import routes, models, errors




