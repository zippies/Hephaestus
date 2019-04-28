#coding:utf-8
from flask import jsonify,request,render_template
from flask_login import current_user, login_required
from ..models import db, Connections, CodeTemplates
from . import url
from lib.methods import autodata,autodate
from config import Config
import traceback
import sqlalchemy
import random


@url.route("/dataTool/addConnection",methods=["POST"])
@login_required
def addConnection():
    info = {"success":True,"errorMsg":None}
    try:
        name = request.form.get("name")
        host = request.form.get("host")
        port = request.form.get("port")
        schema = request.form.get("schema")
        user = request.form.get("username")
        passwd = request.form.get("password")
        print name,host,port,schema,user,passwd
        if not name or not host or not port or not schema or not user or not passwd:
            raise Exception("内容不能为空")
        if Connections.query.filter_by(name=name).all():
            raise Exception("名称已存在")
        conn = Connections(name, host, port, schema, user, passwd, current_user.id)
        db.session.add(conn)
        db.session.commit()
        info["id"] = conn.id
        info["name"] = name
    except Exception as e:
        info["success"] = False
        info["errorMsg"] = str(e)
    finally:
        return jsonify(info)


@url.route("/dataTool/getConnection")
@login_required
def getConnectionInfo():
    info = {"success":True,"errorMsg":None}
    try:
        id = request.args.get("id")
        conn = Connections.query.filter_by(id=id).filter_by(userid=current_user.id).first()
        if conn:
            info["host"] = conn.host
            info["port"] = conn.port
            info["schema"] = conn.schema
            info["username"] = conn.username
            info["password"] = conn.password
        else:
            info["success"] = False
            info["errorMsg"] = "改配置不存在或已被删除"
    except Exception as e:
        info["success"] = False
        info["errorMsg"] = str(e)
    finally:
        print info
        return jsonify(info)


@url.route("/dataTool")
@login_required
def dataTool():
    dbs = Connections.query.filter_by(userid=current_user.id).all()
    codes = CodeTemplates.query.filter_by(userid=current_user.id).all()
    colors = Config.colors
    random.shuffle(colors)
    return render_template("dataTool.html", dbs=dbs, codes=codes, colors=colors)


@url.route("/dataTool/execute",methods=["POST"])
@login_required
def execute():
    info = {"success":True,"errorMsg":None}
    code = request.form.get("code")
    a.host = request.form.get("host")
    a.port = request.form.get("port")
    a.db = request.form.get("schema")
    a.user = request.form.get("user")
    a.passwd = request.form.get("passwd")
    try:
        exec(code)
    except sqlalchemy.exc.OperationalError:
        info["success"] = False
        info["errorMsg"] = "数据库连接异常"
    except Exception as e:
        info["success"] = False
        info["errorMsg"] = "%s:%s" %(str(e),traceback.format_exc())
        print type(e),traceback.format_exc()

    return jsonify(info)


@url.route("/dataTool/save", methods=["POST"])
@login_required
def saveToolTemplate():
    info = {"success": True, "errorMsg": None}
    try:
        name = request.form.get("name")
        content = request.form.get("content")
        edit = request.form.get("edit")
        print name,content
        if not name or not content:
            raise Exception("内容不能为空")
        code = CodeTemplates.query.filter_by(name=name).filter_by(userid=current_user.id).first()
        print 11111,code,edit
        if code and edit == "true":
            code.content = content
            db.session.add(code)
            db.session.commit()
        elif code:
            print "here",edit
            info["success"] = False
            info["errorMsg"] = "exists"
        else:
            code = CodeTemplates(name, content, current_user.id)
            db.session.add(code)
            db.session.commit()
            info["id"] = code.id
            info["name"] = name
    except Exception as e:
        info["success"] = False
        info["errorMsg"] = str(e)
    finally:
        return jsonify(info)


@url.route("/dataTool/delete/<name>", methods=["DELETE"])
@login_required
def deleteCodeTemplate(name):
    info = {"success":True,"errorMsg":None}
    try:
        ct = CodeTemplates.query.filter_by(name=name).filter_by(userid=current_user.id).first()
        if ct:
            info["id"] = ct.id
            db.session.delete(ct)
            db.session.commit()
    except Exception as e:
        info["success"] = False
        info["errorMsg"] = str(e)
    finally:
        return jsonify(info)


@url.route("/dataTool/getTemplate")
@login_required
def getToolTemplateInfo():
    info = {"success":True,"errorMsg":None}
    try:
        id = request.args.get("id")
        ct = CodeTemplates.query.filter_by(id=id).filter_by(userid=current_user.id).first()
        if ct:
            info["name"] = ct.name
            info["content"] = ct.content
        else:
            info["success"] = False
            info["errorMsg"] = "该代码不存在或已被删除"
    except Exception as e:
        info["success"] = False
        info["errorMsg"] = str(e)
    finally:
        return jsonify(info)


@url.route("/dataTool/help")
def dataToolHelp():
    return render_template("dataTool_help.html")
