#coding:utf-8
from flask import jsonify, request, render_template, abort
from flask_login import login_required, current_user
from ..models import db, DataTemplates, User
from . import url
from config import datasample, IP, PORT, Config
from lib.methods import deallist, genData, autodata, autodate
import traceback
import json
import requests
import random


class Executor(object):
    def __init__(self, url=Config.ds_upsert_url):
        self.url = url

    def invoke_ds(self, sql):
        r = requests.post(self.url, json={"ticket": Config.ds_ticket, "data": sql})
        assert r.status_code == 200, "DS调用失败：%s" % r.reason

    def execute(self, sql):
        print sql
        self.invoke_ds(sql)

    def parseSql(self, table, item):
        valuelist = []
        keys = ",".join([i.split("|")[0] for i in item.keys()])
        for i, v in enumerate(item.values()):
            if item.keys()[i].endswith("|int") or item.keys()[i].endswith("|double"):
                valuelist.append(v or "null")
            else:
                valuelist.append("'%s'" % v.replace("'","\\'"))
        values = ",".join(valuelist)
        sql = "upsert into {table}({keys}) values({values})".format(
            table=table,
            keys=keys,
            values=values
        )
        return sql

    def parseTemplate(self, dataTemplate):
        """生成模板数据"""
        datas = deallist(dataTemplate)
        sampleStr = json.dumps(datas)
        self.datas = genData(sampleStr)
        return self.datas

    def executeTemplate(self, data):
        main = data.get("base")
        datastr = json.dumps(data)
        for k, v in main.items():
            datastr = datastr.replace("{%s}" % k, v)

        data = json.loads(datastr)
        self.data = data

        for table, define in data.get("tables").items():
            if isinstance(define, list):
                for item in define:
                    sql = self.parseSql(table, item)
                    print sql
                    self.execute(sql)
            else:
                sql = self.parseSql(table, define)
                print sql
                self.execute(sql)


@url.route("/dataBank")
@login_required
def databank():
    datas = DataTemplates.query.filter_by(userid=current_user.id).all()
    colors = Config.colors
    random.shuffle(colors)
    return render_template("dataBank.html", datas=datas, sample=datasample, colors=colors)


@url.route("/dataBank/generate",methods=["POST"])
def generate():
    """生成模板数据"""
    info = {"success":True,"errorMsg":None,"data":None}
    try:
        data = request.json.get("data") if request.json else eval(request.form.get("data").encode("utf-8"))
        count = None
        if request.json:
            count = request.json.get("count") or 20
        else:
            count = request.form.get("count") or 20
        datas = deallist(data)
        sampleStr = json.dumps(datas,encoding="utf-8",ensure_ascii=False)
        datas = genData(sampleStr, 100)
        info["data"] = datas[:count]
    except Exception as e:
        info["success"] = False
        info["errorMsg"] = "解析异常:" + str(e) + traceback.format_exc()
    finally:
        return jsonify(info)


@url.route("/dataBank/share", methods=["POST"])
def dataBankShare():
    info = {"success": True, "errorMsg": None}
    ulist = request.form.get("ulist").split(",") if request.form.get("ulist") else []
    dt_id = request.form.get("templateId")
    if ulist and dt_id:
        dt = DataTemplates.query.filter_by(id=int(dt_id)).filter_by(userid=current_user.id).first()
        userlist = [u for u in [User.query.filter_by(nickname=u).first() for u in ulist] if u]
        if dt:
            for user in userlist:
                newtemplate = DataTemplates(
                    name=dt.name,
                    content=dt.content,
                    userid=user.id
                )
                db.session.add(newtemplate)
            db.session.commit()
        else:
            info["success"] = False
            info["errorMsg"] = "模板不存在或已被删除"
    else:
        info["success"] = False
        info["errorMsg"] = "分享用户列表不能为空"

    return jsonify(info)


@url.route("/dataBank/hbase/insert/<int:id>", methods=["POST"])
def hbaseInsert(id):
    info = {"success": True, "errorMsg": None}
    dt = DataTemplates.query.filter_by(id=id).filter_by(userid=current_user.id).first()
    if dt:
        datatemplate = json.loads(dt.content)
        if not datatemplate.get("tables", None):
            info["success"] = False
            info["errorMsg"] = "未解析到相关表结构!"
        else:
            try:
                executor = Executor()
                datas = executor.parseTemplate(datatemplate)
                executor.executeTemplate(datas[0] if len(datas) == 1 else datas)
            except Exception as e:
                info["success"] = False
                info["errorMsg"] = "入库异常:" + str(e) + traceback.format_exc()
    else:
        info["success"] = False
        info["errorMsg"] = "模板不存在或已被删除"

    return jsonify(info)


@url.route("/databank/insert", methods=["POST"])
def insert_hbash():
    info = {"success": True, "errorMsg": None}
    datatemplate = request.json
    if not datatemplate.get("tables", None):
        info["success"] = False
        info["errorMsg"] = "未解析到相关表结构!"
    else:
        try:
            executor = Executor()
            datas = executor.parseTemplate(datatemplate)
            executor.executeTemplate(datas[0] if len(datas) == 1 else datas)
        except Exception as e:
            info["success"] = False
            info["errorMsg"] = "入库异常:" + str(e) + traceback.format_exc()
    return jsonify(info)


@url.route("/dataBank/help")
def help():
    """帮助页面"""
    return render_template("help.html", ip=IP, port=PORT)


@url.route("/autodata",methods=["POST"])
def generateData():
    """外部使用接口，调用内部autodata方法"""
    info = {"success": True, "errorMsg": None, "data": None}
    try:
        itype = request.json.get("type") if request.json else request.form.get("type")
        length = request.json.get("length") or (7,10) if request.json else request.form.get("length") or (7,10)
        age = request.json.get("age") if request.json else request.form.get("age")
        sex = request.json.get("sex") if request.json else request.form.get("sex")
        samples = request.json.get("samples") or [] if request.json else request.form.get("type") or []
        count = request.json.get("count") if request.json else request.form.get("count")
        if count:
            datalist = []
            count = int(count)
            for i in range(count):
                data = autodata(type=itype,samples=samples,length=length,age=age,sex=sex)
                datalist.append(data)
                info["data"] = data
        else:
            data = autodata(type=itype,samples=samples,length=length,age=age,sex=sex)
            info["data"] = data
    except Exception as e:
        print traceback.format_exc()
        info["success"] = False
        info["errorMsg"] = str(e) + traceback.format_exc()
    finally:
        return jsonify(info)


@url.route("/autodate",methods=["POST"])
def generateDate():
    """外部使用接口，调用内部autodate方法"""
    info = {"success":True,"errorMsg":None,"data":None}
    datelist = []
    try:
        start = request.json.get("start") if request.json else request.form.get("start")
        step = int(request.json.get("step")) if request.json else int(request.form.get("step"))
        datetype = request.json.get("datetype") if request.json else request.form.get("datetype")
        informat = request.json.get("informat") if request.json else request.form.get("informat")
        outformat = request.json.get("outformat") if request.json else request.form.get("outformat")
        count = request.json.get("count") if request.json else request.form.get("count")
        count = int(count)
        for i in range(count):
            idate = autodate(counter=i,start=start,step=step,datetype=datetype,informat=informat,outformat=outformat)
            datelist.append(idate)
        info["data"] = datelist
    except Exception as e:
        print traceback.format_exc()
        info["success"] = False
        info["errorMsg"] = str(e) + traceback.format_exc()
    finally:
        return jsonify(info)


@url.route("/dataBank/save", methods=["POST"])
@login_required
def saveBankTemplate():
    """保存模板"""
    info = {"success": True, "errorMsg": None}
    try:
        name = request.form.get("name")
        content = request.form.get("content")
        edit = request.form.get("edit")
        print name,content
        if not name or not content:
            raise Exception("内容不能为空")
        data = DataTemplates.query.filter_by(name=name).filter_by(userid=current_user.id).first()
        if data and edit == "true":
            data.content = content
            db.session.add(data)
            db.session.commit()
        elif data:
            info["success"] = False
            info["errorMsg"] = "exists"
        else:
            data = DataTemplates(name, content, current_user.id)
            db.session.add(data)
            db.session.commit()
            info["id"] = data.id
            info["name"] = name
    except Exception as e:
        info["success"] = False
        info["errorMsg"] = str(e)
    finally:
        return jsonify(info)


@url.route("/dataBank/delete/<name>", methods=["DELETE"])
@login_required
def deleteDataTemplate(name):
    """删除模板"""
    info = {"success":True,"errorMsg":None}
    try:
        dt = DataTemplates.query.filter_by(name=name).filter_by(userid=current_user.id).first()
        if dt:
            info["id"] = dt.id
            db.session.delete(dt)
            db.session.commit()
    except Exception as e:
        info["success"] = False
        info["errorMsg"] = str(e)
    finally:
        return jsonify(info)


@url.route("/dataBank/getTemplate")
@login_required
def getBankTemplateInfo():
    """内部前端切换模板数据时调用，获取模板"""
    info = {"success":True,"errorMsg":None}
    try:
        id = request.args.get("id")
        dt = DataTemplates.query.filter_by(id=id).filter_by(userid=current_user.id).first()
        if dt:
            info["name"] = dt.name
            info["content"] = dt.content
        else:
            info["success"] = False
            info["errorMsg"] = "该代码不存在或已被删除"
    except Exception as e:
        info["success"] = False
        info["errorMsg"] = str(e)
    finally:
        return jsonify(info)


@url.route("/dataBank/template")
def getBankData():
    """外部使用，调用模板的生成数据"""
    name = request.args.get("name")
    print name
    dt = DataTemplates.query.filter_by(name=name).first()
    print dt
    if dt:
        data = json.loads(dt.content)
        datas = deallist(data)
        sampleStr = json.dumps(datas,encoding="utf-8",ensure_ascii=False)
        datas = genData(sampleStr, 100)
        return jsonify(datas)
    else:
        abort(404)


@url.route("/dataBank/hbase/template", methods=["POST"])
def descHbaseTable():
    """外部使用，获取hbase表字段描述"""
    meta_url = "http://%s/api/phoenix/meta/{db}/{table}" % Config.xmeta_host
    baseTemplate = {
        "base": {
            "uid": "",
            "aid": "",
        },
        "tables": {
        }
    }
    tables = request.json.get("tables")

    for db_table in tables:
        db, table = db_table.upper().split(".")
        url = meta_url.format(db=db, table=table)
        resp = requests.get(url)
        if resp.status_code == 200 and resp.json()["columns"]:
            tableitem = {}
            for column in resp.json()["columns"]:
                if column.get("tpe") in ["BIGINT", "INTEGER"]:
                    tableitem["%s|int" % column.get("name")] = column.get("comment")
                elif column.get("tpe") == "DOUBLE":
                    tableitem["%s|double" % column.get("name")] = column.get("comment")
                else:
                    tableitem[column.get("name")] = column.get("comment")
            baseTemplate["tables"][db_table.upper()] = tableitem
        else:
            print "none exists"

    return jsonify(baseTemplate)