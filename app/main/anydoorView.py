#coding:utf-8
from flask import request,render_template,jsonify,redirect,url_for,flash
from flask_login import login_required, current_user
from mailer import anydoor_notice
from urllib import quote
from config import Config
import traceback
from ..models import db,Keeper,Door
from . import url
import time


@url.route("/anydoor")
@login_required
def keepers():
    return render_template("keeper.html")


@url.route("/anydoor/keeper/add",methods=["POST"])
@login_required
def addKeeper():
    message = {"type": "success", "message": "新增成功！"}
    name = request.form.get("name")
    desc = request.form.get("desc")
    try:
        ca = Keeper.query.filter_by(name=name).filter_by(status=0).first()
        if not ca:
            keeper = Keeper(name=name, desc=desc, creator=current_user.nickname)
            db.session.add(keeper)
            db.session.commit()
        else:
            message = {"type":"error","message":"[error]:'%s'名称已被占用！" %name}
    except Exception as e:
        message = {"type":"error","message":"[error]:%s|%s" %(str(e),traceback.format_exc())}

    flash(message)
    return redirect(url_for("main.keepers"))

@url.route("/anydoor/keeper/edit/<int:id>", methods=["POST"])
def editKeeper(id):
    message = {"type": "success", "message": "保存成功！"}
    try:
        keeper = Keeper.query.filter_by(id=id).filter_by(status=0).first()
        if keeper:
            name = request.form.get("name")
            desc = request.form.get("desc")
            keeper.name = name.strip()
            keeper.desc = desc.strip()
            db.session.add(keeper)
            db.session.commit()
        else:
            message = {"type": "error", "message": "该分类不存在或已被删除"}
    except Exception as e:
        message = {"type": "error", "message": "[error]:%s|%s" % (str(e), traceback.format_exc())}
    finally:
        flash(message)
        return redirect(url_for("main.keepers"))


@url.route("/anydoor/keeper/all")
@login_required
def allKeeper():
    keepers = Keeper.query.filter_by(status=0).all()
    data = [
        {
            "id": i + 1,
            "name": "<a href='/anydoor/%s/'>%s</a>" % (c.id, c.name),
            "desc": c.desc,
            "operation":"""<a href='#' id='follow_%s' onclick='follow(%s, %s)' style='display: %s'>关注</a> \
            <a href='#' id='cancelfollow_%s' onclick='cancelfollow(%s, %s)' style='display: %s'>取消关注</a> \
            <a href='#' onclick="edit(%s,'%s','%s')">编辑</a>\
            <a href='#' onclick='del(%s)'>删除</a>""" % (
                i, i, c.id, "" if c.followers is None or current_user.nickname not in eval(c.followers) else "none",
                i, i, c.id, "none" if c.followers is None or current_user.nickname not in eval(c.followers) else "",
                c.id, quote(str(c.name)), quote(str(c.desc)),
                c.id
            ),
            "creator": c.creator
        } for i, c in enumerate(keepers)
    ]

    return jsonify(data)


@url.route("/anydoor/keeper/delete/<id>",methods=["delete"])
@login_required
def delKeeper(id):
    info = {"result":True,"errorMsg":None}
    try:
        keeper = Keeper.query.filter_by(id=id).first()
        if keeper:
            if keeper.creator != current_user.nickname:
                info["result"] = False
                info["errorMsg"] = "非创建者没有权限删除"
            else:
                keeper.status = -1
                db.session.add(keeper)
                db.session.commit()
                message = {"type":"success","message":"'%s'删除成功!" %keeper.name}
                flash(message)
    except Exception as e:
        info["result"] = False
        info["errorMsg"] = "[error]:%s|%s" %(str(e),traceback.format_exc())
    finally:
        return jsonify(info)


@url.route("/anydoor/<keeperid>/")
@login_required
def viewKeeper(keeperid):
    keeper = Keeper.query.filter_by(id=keeperid).filter_by(status=0).first()
    if keeper:
        return render_template("door.html",keeperid=keeperid,keepername=keeper.name)
    else:
        return render_template("404.html")


@url.route("/anydoor/<keeperid>/add",methods=["post"])
@login_required
def addDoor(keeperid):
    message = {"type": "success", "message": "新增成功！"}

    desc = request.form.get("desc")
    link = request.form.get("link")
    other = request.form.get("other")
    try:
        keeper = Keeper.query.filter_by(id=keeperid).filter_by(status=0).first()
        if keeper:
            d = Door.query.filter_by(desc=desc).filter_by(status=0).all()
            door = Door(
                desc="%s_%s" %(desc,len(d)) if d else desc,
                link=link,
                other=other,
                keeperid=keeperid,
                creator=current_user.nickname
            )
            db.session.add(door)
            db.session.commit()
            mails = []
            followers = eval(keeper.followers)
            if followers:
                for fl in followers:
                    mails.append(fl + Config.EMAIL_SUFFIX)
                anydoor_notice.delay(
                    keeper.name,
                    desc,
                    link,
                    other,
                    current_user.nickname,
                    "http://%s/anydoor/%s" %(Config.DOMAIN, keeperid),
                    mails
                )
        else:
            message = {"type":"error","message":"新增失败,该分类不存在或已被删除！"}
    except Exception as e:
        message = {"type":"error","message":"新增失败,errorMsg:%s|%s" %(str(e),traceback.format_exc())}

    flash(message)
    return redirect(url_for("main.viewKeeper",keeperid=keeperid))


@url.route("/anydoor/<keeperid>/edit/<int:id>", methods=["POST"])
def editDoor(keeperid, id):
    message = {"type": "success", "message": "保存成功！"}
    try:
        keeper = Keeper.query.filter_by(id=keeperid).filter_by(status=0).first()
        if keeper:
            door = Door.query.filter_by(id=id).filter_by(status=0).first()
            if door:
                desc = request.form.get("desc")
                link = request.form.get("link")
                other = request.form.get("other")
                door.desc = desc.strip()
                door.link = link.strip()
                door.other = other.strip()
                db.session.add(door)
                db.session.commit()
                mails = []
                followers = eval(keeper.followers)
                if followers:
                    for fl in followers:
                        mails.append(fl + Config.EMAIL_SUFFIX)
                    anydoor_notice.delay(
                        keeper.name,
                        desc,
                        link,
                        other,
                        current_user.nickname,
                        "http://%s/anydoor/%s" % (Config.DOMAIN, keeperid),
                        mails,
                        edit=True
                    )
            else:
                message = {"type": "error", "message": "该资源链接不存在或已被删除"}
        else:
            message = {"type": "error", "message": "该分类不存在或已被删除"}
    except Exception as e:
        message = {"type": "error", "message": "[error]:%s|%s" % (str(e), traceback.format_exc())}
    finally:
        flash(message)
        return redirect(url_for("main.viewKeeper",keeperid=keeperid))


@url.route("/anydoor/<keeperid>/all")
@login_required
def allDoor(keeperid):
    doors = Door.query.filter_by(keeperid=keeperid).filter_by(status=0).all()
    data = [
        {
            "id":i+1,"desc":"%s" %d.desc,
            "link":"<a href='%s' target='_blank'>%s</a>" %(d.link,d.link),
            "other":"<a id='show-hide-{id}' onclick='toggleThis({id})' href='javascript:;'>显示</a>\
            <textarea id='other-{id}' class='form-control' style='display:none;max-width:400px;min-height:150px;max-height:250px;' placeholder='数据库连接信息/日志服务器路径/登录用户账号等'>{other}</textarea>\
            <a id='save-{id}' href='javascript:;' onclick='saveEdit({keeperid}, {id})' style='display:none'>修改</a>".format(
                id=d.id, other=d.other, keeperid=keeperid
            ),
            "creator": d.creator,
            "operation": """<a href='#' onclick="edit(%s, %s, '%s', '%s', '%s')">编辑</a> <a href='#' onclick='del(%s)'>删除</a>""" % (
                keeperid, d.id, quote(str(d.desc)), quote(str(d.link)), quote(str(d.other)), d.id
            )
        } for i,d in enumerate(doors)
    ]
    return jsonify(data)


@url.route("/anydoor/door/delete/<id>",methods=["delete"])
@login_required
def delDoor(id):
    info = {"result":True,"errorMsg":None}
    try:
        door = Door.query.filter_by(id=id).first()
        if door:
            if door.creator != current_user.nickname:
                info["result"] = False
                info["errorMsg"] = "非创建者没有权限删除"
            else:
                door.status = -1
                db.session.add(door)
                db.session.commit()
                message = {"type":"success","message":"'%s'删除成功!" %door.desc}
                flash(message)
    except Exception as e:
        info["result"] = False
        info["errorMsg"] = "[error]%s|%s" %(str(e),traceback.format_exc())
    finally:
        return jsonify(info)


@url.route("/anydoor/<keeperid>/modify/<id>",methods=["POST"])
@login_required
def modifyDoor(keeperid, id):
    info = {"result":True,"errorMsg":None}
    try:
        keeper = Keeper.query.filter_by(id=keeperid).filter_by(status=0).first()
        if keeper:
            other = request.form.get("other")
            door = Door.query.filter_by(id=id).filter_by(status=0).first()
            if door:
                door.other = other
                db.session.add(door)
                db.session.commit()
                mails = []
                followers = eval(keeper.followers)
                if followers:
                    for fl in followers:
                        mails.append(fl + Config.EMAIL_SUFFIX)
                    anydoor_notice.delay(
                        keeper.name,
                        door.desc,
                        door.link,
                        other,
                        current_user.nickname,
                        "http://%s/anydoor/%s" % (Config.DOMAIN, keeperid),
                        mails,
                        edit=True
                    )
            else:
                info["result"] = False
                info["errorMsg"] = "指定修改的对象不存在或已被删除"
        else:
            info["result"] = False
            info["errorMsg"] = "指定修改的分类不存在或已被删除"
    except Exception as e:
        info["result"] = False
        info["errorMsg"] = "[error]%s|%s" %(str(e),traceback.format_exc())
    finally:
        return jsonify(info)


@url.route("/anydoor/keeper/follow/<int:id>")
def follow(id):
    info = {"result":True,"errorMsg":None}

    try:
        keeper = Keeper.query.filter_by(id=id).first()
        if keeper:
            keeper.addFollower(current_user.nickname)
            print time.strftime("%Y-%m-%d %H:%M:%S"), "before commit:", keeper.followers
            db.session.add(keeper)
            db.session.commit()
            print time.strftime("%Y-%m-%d %H:%M:%S"), "after commit:", keeper.followers
        else:
            info["result"] = False
            info["errorMsg"] = "指定的对象不存在或已被删除"
    except Exception as e:
        info["result"] = False
        info["errorMsg"] = "[error]%s|%s" % (str(e), traceback.format_exc())
    finally:
        return jsonify(info)


@url.route("/anydoor/keeper/cancelfollow/<int:id>")
def cancelfollow(id):
    info = {"result":True,"errorMsg":None}

    try:
        keeper = Keeper.query.filter_by(id=id).first()
        if keeper:
            keeper.delFollower(current_user.nickname)
            db.session.add(keeper)
            db.session.commit()
        else:
            info["result"] = False
            info["errorMsg"] = "指定的对象不存在或已被删除"
    except Exception as e:
        info["result"] = False
        info["errorMsg"] = "[error]%s|%s" % (str(e), traceback.format_exc())
    finally:
        return jsonify(info)