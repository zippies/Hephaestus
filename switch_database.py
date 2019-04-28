#encoding:utf-8
from sqlalchemy import Column, String, Integer, PickleType, DateTime, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

Base = declarative_base()

class Tool(Base):
    __tablename__ = "tool"
    __table_args__ = {'mysql_charset': 'utf8'}
    id = Column(Integer, primary_key=True)
    name = Column(String(32))
    brief_introductions = Column(PickleType)
    suitables = Column(PickleType)
    href = Column(String(128))
    userid = Column(Integer)
    status = Column(Integer, default=0)
    createdtime = Column(DateTime, default=datetime.now)

    def __init__(self, name, brief_introductions, suitables, href):
        self.name = name.encode('utf-8')
        self.brief_introductions = brief_introductions
        self.suitables = suitables
        self.href=href

class User(Base):
    __tablename__ = "user"
    __table_args__ = {'mysql_charset': 'utf8'}
    id = Column(Integer, primary_key=True)
    nickname = Column(String(32))
    password = Column(String(128), default="123456")
    ip = Column(String(64))
    createdtime = Column(DateTime, default=datetime.now)

    def __init__(self, nickname, password, ip):
        self.nickname = nickname.encode('utf-8')
        self.password = password
        self.ip = ip

    def __repr__(self):
        return "<User:%s>" % self.nickname


class Keeper(Base):
    __tablename__ = "keeper"
    __table_args__ = {'mysql_charset': 'utf8'}

    id = Column(Integer, primary_key=True)
    name = Column(String(32))
    desc = Column(String(128))
    status = Column(Integer, default=0)
    creator = Column(String(32))
    followers = Column(String(256), default="[]")
    createdtime = Column(DateTime, default=datetime.now)

    def __init__(self, name, desc, creator):
        self.name = name.encode('utf-8')
        self.desc = desc.encode('utf-8')
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


class Door(Base):
    __tablename__ = "door"
    __table_args__ = {'mysql_charset': 'utf8'}

    id = Column(Integer, primary_key=True)
    desc = Column(String(32))
    link = Column(String(256))
    other = Column(String(1280))
    keeperid = Column(Integer)
    status = Column(Integer, default=0)
    creator = Column(String(32))
    createdtime = Column(DateTime, default=datetime.now)

    def __init__(self, desc, link, other, keeperid, creator):
        self.desc = desc
        self.link = link
        self.other = other
        self.keeperid = keeperid
        self.creator = creator

    def __repr__(self):
        return "<Door:%s>" % self.desc


class Connections(Base):
    __tablename__ = "connections"
    __table_args__ = {'mysql_charset': 'utf8'}

    id = Column(Integer, primary_key=True)
    name = Column(String(12))
    host = Column(String(128))
    port = Column(Integer)
    schema = Column(String(32))
    username = Column(String(32))
    password = Column(String(128))
    userid = Column(Integer)
    createdtime = Column(DateTime, default=datetime.now)

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


class DataTemplates(Base):
    __tablename__ = "data_templates"
    __table_args__ = {'mysql_charset': 'utf8'}

    id = Column(Integer, primary_key=True)
    name = Column(String(32))
    content = Column(PickleType)
    userid = Column(Integer)
    createdtime = Column(DateTime, default=datetime.now)

    def __init__(self, name, content, userid):
        self.name = name
        self.content = content
        self.userid = userid

    def __repr__(self):
        return "<DataTemplates:%s>" % self.name


class CodeTemplates(Base):
    __tablename__ = "code_templates"
    __table_args__ = {'mysql_charset': 'utf8'}

    id = Column(Integer, primary_key=True)
    name = Column(String(32))
    content = Column(PickleType)
    userid = Column(Integer)
    createdtime = Column(DateTime, default=datetime.now)

    def __init__(self, name, content, userid):
        self.name = name
        self.content = content
        self.userid = userid

    def __repr__(self):
        return "<CodeTemplates:%s>" % self.name

engine_mysql = create_engine('mysql+pymysql://user:passwd@host:3306/qaops?charset=utf8')
engine_sqlite = create_engine('sqlite:///data.sqlite')
DBSession_mysql = sessionmaker(bind=engine_mysql)
DBSession_sqlite = sessionmaker(bind=engine_sqlite)

session_mysql = DBSession_mysql()
session_sqlite = DBSession_sqlite()


def init_db():
    Base.metadata.drop_all(engine_mysql)
    Base.metadata.create_all(engine_mysql)

# init_db()

tools = session_sqlite.query(Tool).all()
users = session_sqlite.query(User).all()
keepers = session_sqlite.query(Keeper).all()
doors = session_sqlite.query(Door).all()
connections = session_sqlite.query(Connections).all()
data_templates = session_sqlite.query(DataTemplates).all()
code_templates = session_sqlite.query(CodeTemplates).all()


for tool in tools:
    mytool = Tool(
        name = tool.name,
        brief_introductions = tool.brief_introductions,
        suitables = tool.suitables,
        href = tool.href
    )
    mytool.id = tool.id
    mytool.userid = tool.userid
    mytool.status = tool.status
    mytool.createdtime = tool.createdtime
    session_mysql.add(mytool)
    session_mysql.commit()


for user in users:
    myuser = User(
        nickname = user.nickname,
        password = user.password,
        ip = user.ip
    )
    myuser.id = user.id
    myuser.createdtime = user.createdtime
    session_mysql.add(myuser)
    session_mysql.commit()


for k in keepers:
    myk = Keeper(
        name = k.name,
        desc = k.desc,
        creator = k.creator
    )
    myk.id = k.id
    myk.status = k.status
    myk.followers = k.followers
    myk.createdtime = k.createdtime
    session_mysql.add(myk)
    session_mysql.commit()


for d in doors:
    md = Door(
        desc = d.desc,
        link = d.link,
        other = d.other,
        keeperid = d.keeperid,
        creator = d.creator
    )
    md.id = d.id
    md.status = d.status
    md.createdtime = d.createdtime
    session_mysql.add(md)
    session_mysql.commit()


for c in connections:
    mc = Connections(
        name = c.name,
        host = c.host,
        port = c.port,
        schema = c.schema,
        username = c.username,
        password = c.password,
        userid = c.userid
    )
    mc.id = c.id
    mc.createdtime = c.createdtime
    session_mysql.add(mc)
    session_mysql.commit()


for dt in data_templates:
    mdt = DataTemplates(
        name = dt.name,
        content = dt.content,
        userid = dt.userid
    )
    mdt.id = dt.id
    mdt.createdtime = dt.createdtime
    session_mysql.add(mdt)
    session_mysql.commit()


for code in code_templates:
    print code_templates
    mct = CodeTemplates(
        name = code.name,
        content = code.content,
        userid = code.userid
    )
    mct.id = code.id
    mct.createdtime = code.createdtime
    session_mysql.add(mct)
    session_mysql.commit()


