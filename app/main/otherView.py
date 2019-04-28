#coding:utf-8
from flask import render_template, request, redirect, url_for, session, jsonify
from flask_login import login_user, current_user
from ..models import User, db, Tool
from config import Config
from .. import gitlab
from . import url
import random


@url.route("/check_backend_active.html")
def nginx_check():
    return "i'm ok"


@url.route('/')
def index():
    if 'gitlab_token' in session:
        me = gitlab.get('user')
        user = User.query.filter_by(nickname=me.data.get("name")).first()
        tools = Tool.query.filter_by(status=0).all()
        if not user:
            user = User(
                nickname=me.data.get("name"),
                password=me.data.get("private_token"),
                ip=request.remote_addr
            )
            db.session.add(user)
            db.session.commit()

        login_user(user)
        colors = Config.colors
        random.shuffle(colors)
        if len(tools) > len(colors):
            colors.extend(colors)
        return render_template("index.html", tools=tools, colors=colors)
    return redirect(url_for('main.login'))


@url.route('/login')
def login():
    return gitlab.authorize(callback=url_for('main.authorized', _external=True, _scheme='http'))


@url.route('/logout')
def logout():
    del session['gitlab_token']
    return redirect(url_for('main.index'))


@url.route('/login/authorized')
def authorized():
    resp = gitlab.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error'],
            request.args['error_description']
        )
    session['gitlab_token'] = (resp['access_token'], '')
    return redirect(url_for('main.index'))


@gitlab.tokengetter
def get_gitlab_oauth_token():
    return session.get('gitlab_token')


@url.route("/tool/add", methods=["POST"])
def addTool():
    info = {"result": True,"errorMsg": None}
    body = request.json or request.form
    try:
        def add_one_tool(item):
            print item.keys()
            name = item.get("name")
            descriptions = item.get("descriptions") or item.get("briefs[]")
            suitables = item.get("suitables") or item.get("suitables[]")
            href = item.get("href")
            tool = Tool(
                name=name,
                brief_introductions=descriptions,
                suitables=suitables,
                href=href
            )
            try:
                tool.userid = current_user.id
            except:
                pass
            db.session.add(tool)

        if isinstance(body, dict):
            add_one_tool(body)
        elif isinstance(body, list):
            for item in body:
                add_one_tool(item)
        else:
            info["result"] = False
            info["errorMsg"] = "数据格式不正确"
        db.session.commit()
    except Exception as e:
        info["result"] = True
        info["errorMsg"] = str(e)
    finally:
        return jsonify(info)


@url.route("/tool/get/<int:id>")
def getTool(id):
    info = {"result": True, "errorMsg": None}
    try:
        tool = Tool.query.filter_by(id=id).first()
        if tool:
            info["name"] = tool.name
            info["briefs"] = "<br>".join(tool.brief_introductions)
            info["suitables"] = "<br>".join(tool.suitables)
            info["href"] = tool.href
        else:
            info["result"] = False
            info["errorMsg"] = "工具不存在或已被删除"
    except Exception as e:
        info["result"] = False
        info["errorMsg"] = str(e)
    finally:
        return jsonify(info)


@url.route("/tool/edit/<int:id>", methods=["POST"])
def editTool(id):
    info = {"result": True, "errorMsg": None}
    try:
        tool = Tool.query.filter_by(id=id).first()
        if tool:
            name = request.form.get("name")
            briefs = request.form.get("briefs").split("<br>")
            suitables = request.form.get("suitables").split("<br>")
            href = request.form.get("href")
            tool.name = name
            tool.brief_introductions = briefs
            tool.suitables = suitables
            tool.href = href
            db.session.add(tool)
            db.session.commit()
        else:
            info["result"] = False
            info["errorMsg"] = "工具不存在或已被删除"
    except Exception as e:
        info["result"] = False
        info["errorMsg"] = str(e)
    finally:
        return jsonify(info)


@url.route("/tool/delete/<int:id>", methods=["DELETE"])
def deleteTool(id):
    info = {"result": True, "errorMsg": None}
    try:
        tool = Tool.query.filter_by(id=id).first()
        if tool:
            db.session.delete(tool)
            db.session.commit()
        else:
            info["result"] = False
            info["errorMsg"] = "工具不存在或已被删除"
    except Exception as e:
        info["result"] = False
        info["errorMsg"] = str(e)
    finally:
        return jsonify(info)
