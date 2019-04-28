# -*- coding: utf-8 -*-
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_oauthlib.client import OAuth

app = Flask(__name__)
db = SQLAlchemy()
login_manager = LoginManager()
oauth = OAuth(app)

gitlab = oauth.remote_app('gitlab',
    base_url='http://git.caimi-inc.com/api/v3/',
    request_token_url=None,
    access_token_url='http://git.caimi-inc.com/oauth/token',
    authorize_url='http://git.caimi-inc.com/oauth/authorize',
    access_token_method='POST',
    consumer_key='27a73f1f5478c9243a838730015fd65643d606ef136945da51f9cb91121717db',
    consumer_secret='9f7a52128ad0743895bc52891f457eb6fe7a1951a304c9b35f9a7eaa57af850d'
)


def createApp():
    config = Config()
    app.config.from_object(config)
    db.init_app(app)
    login_manager.init_app(app)
    from .main import url as BluePrint
    app.register_blueprint(BluePrint)

    return app