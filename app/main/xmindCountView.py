# -*- encoding:utf-8 -*-
from flask import render_template, request
from werkzeug.utils import secure_filename
from flask_login import login_required
from config import Config
from . import url
import xmind
import os

@url.route("/xmindCaseCounter", methods=["GET", "POST"])
@login_required
def xmindCaseCounter():
    caseCount = 0
    filename = None
    if request.method == 'POST' and 'xmind' in request.files:
        f = request.files['xmind']
        secure_file_name = secure_filename(f.filename)
        file_path = os.path.join(Config.UPLOAD_FOLDER, secure_file_name+".xmind")
        f.save(file_path)
        workbook = xmind.load(file_path)
        root = workbook.documentElement
        first = root.firstChild.childNodes[0]
        caseCount = first.toxml().count("</title></topic>")
        filename = f.filename

    return render_template("xmind.html", caseCount=caseCount, filename=filename)