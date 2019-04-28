#coding:utf-8
from flask import jsonify, render_template, request, redirect
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from ..models import db, PipPackages
from . import url
from config import Config
import os


@url.route("/pipsource")
def pipSource():
    pp = PipPackages.query.filter_by(type=1).all()
    return render_template("pipSource.html", usersources=pp)


@url.route("/pipsource/latest")
def getPipSource():
    info = {"packages": None, "locals": None}
    pp = PipPackages.query.filter_by(status=0).all()
    packages = set()
    locals = set()
    if pp:
        for p in pp:
            if p.type == 1:
                locals.update([i for i in p.packages.split("\r\n") if i.strip()])
            else:
                packages.update([i for i in p.packages.split("\r\n") if i.strip()])
            p.status = 1
            db.session.add(p)

        db.session.commit()

    info["packages"] = list(packages)
    info["locals"] = list(locals)

    return jsonify(info)


@url.route("/pipsource/add", methods=["POST"])
@login_required
def addPipSource():
    info = {"result": True, "errorMsg": None}
    try:
        packages = request.form.get("packages").strip()
        pp = PipPackages(
            packages=packages,
            userid=current_user.id
        )
        f = request.files["local"]
        if f.filename:
            for ftypes in Config.SUPPORT_PACKAGES:
                if f.filename.endswith(ftypes):
                    break
            else:
                info["result"] = False
                info["errorMsg"] = "暂不支持上传该类型文件"
                return jsonify(info)
            fname = secure_filename(f.filename)
            f.save(os.path.join(Config.UPLOAD_FOLDER, fname))
            pp.type = 1
            pp.packages += "\r\n%s" %fname
        db.session.add(pp)
        db.session.commit()
    except Exception as e:
        info["result"] = False
        info["errorMsg"] = str(e)
    finally:
        return jsonify(info)