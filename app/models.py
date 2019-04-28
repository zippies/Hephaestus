# -*- coding: utf-8 -*-
from datetime import datetime
from flask_login import UserMixin
from . import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()


login_manager.session_protection = "strong"
login_manager.login_view = "main.login"
login_manager.login_message = {"type":"error","message":"请登录后使用该功能"}


class Tool(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    brief_introductions = db.Column(db.PickleType)
    suitables = db.Column(db.PickleType)
    href = db.Column(db.String(128))
    userid = db.Column(db.Integer)
    status = db.Column(db.Integer, default=0)
    createdtime = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, name, brief_introductions, suitables, href):
        self.name = name
        self.brief_introductions = brief_introductions
        self.suitables = suitables
        self.href=href

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(32))
    password = db.Column(db.String(128), default="123456")
    ip = db.Column(db.String(64))
    createdtime = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, nickname, password, ip):
        self.nickname = nickname
        self.password = password
        self.ip = ip

    def __repr__(self):
        return "<User:%s>" % self.nickname


class Keeper(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    desc = db.Column(db.String(128))
    status = db.Column(db.Integer, default=0)
    creator = db.Column(db.String(32))
    followers = db.Column(db.String(256), default="[]")
    createdtime = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, name, desc, creator):
        self.name = name
        self.desc = desc
        self.creator = creator

    def addFollower(self,followername):
        if not self.followers:
            self.followers = '[]'
        tmp = eval(self.followers)
        if followername not in tmp:
            tmp.append(followername)
            self.followers = str(tmp)

    def delFollower(self,followername):
        followers = eval(self.followers)
        if followername in followers:
            followers.remove(followername)
            self.followers = str(followers)

    def __repr__(self):
        return "<Keeper:%s:%s>" % (self.name, self.desc)


class Door(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    desc = db.Column(db.String(32))
    link = db.Column(db.String(256))
    other = db.Column(db.String(1280))
    keeperid = db.Column(db.Integer)
    status = db.Column(db.Integer, default=0)
    creator = db.Column(db.String(32))
    createdtime = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, desc, link, other, keeperid, creator):
        self.desc = desc
        self.link = link
        self.other = other
        self.keeperid = keeperid
        self.creator = creator

    def __repr__(self):
        return "<Door:%s>" % self.desc


class Connections(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(12))
    host = db.Column(db.String(128))
    port = db.Column(db.Integer)
    schema = db.Column(db.String(32))
    username = db.Column(db.String(32))
    password = db.Column(db.String(128))
    userid = db.Column(db.Integer)
    createdtime = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, name, host, port, schema, username, password, userid):
        self.name = name
        self.host = host
        self.port = port
        self.schema = schema
        self.username = username
        self.password = password
        self.userid = userid

    def __repr__(self):
        return "<Connections:%s>" % self.name


class DataTemplates(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    content = db.Column(db.PickleType)
    userid = db.Column(db.Integer)
    createdtime = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, name, content, userid):
        self.name = name
        self.content = content
        self.userid = userid

    def __repr__(self):
        return "<DataTemplates:%s>" % self.name


class CodeTemplates(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    content = db.Column(db.PickleType)
    userid = db.Column(db.Integer)
    createdtime = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, name, content, userid):
        self.name = name
        self.content = content
        self.userid = userid

    def __repr__(self):
        return "<CodeTemplates:%s>" % self.name


class PipPackages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    packages = db.Column(db.Text)
    type = db.Column(db.Integer, default=0) # 0: 第三方  1： 本地上传
    userid = db.Column(db.Integer)
    status = db.Column(db.Integer, default=0)
    createdtime = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, packages, userid):
        self.packages = packages
        self.userid = userid

    def __repr__(self):
        return "<PipPackages:%s>" % self.createdtime

    @property
    def username(self):
        user = User.query.filter_by(id=self.userid).first()
        if user:
            return user.nickname
        else:
            return ""

