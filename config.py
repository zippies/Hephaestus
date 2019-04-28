# -*- coding: utf-8 -*-
import socket, os

IP = "host"
PORT = 8888
hostname = socket.gethostname()
islocal = False


class Config:
    DEBUG = True
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), "app/static/downloads")
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://user:passwd@host:3306/qaops?charset=utf8' if not islocal else "sqlite:///" + os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 'data.sqlite')
    BROKER_URL = "redis://host:6379/0"
    SECRET_KEY = 'what does the fox say?'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_POOL_RECYCLE = 5
    EMAIL_SUFFIX = "@company.com"
    DOMAIN = "host"
    SUPPORT_PACKAGES = [".tar.gz", ".whl", ".zip", ".egg"]
    ci_job_name = "ci_automation_runner"

    ds_ticket = ""
    ds_upsert_url = "http://ds/phoenix/upsert"

    repo_mapping = {
        "": "case/it/module/"
    }

    colors = [
        "#F1FAFA", "#E8FFE8", "#E8E8FF", "#E8D098", "#EFEFDA", "#CCFFFF"
    ]

    xmeta_host = ""


datasample = """
{
    "user_brief": {
        "user_sid": "autodata(type='int',length=9)",
        "phone": "autodata(type='phone')",
        "gps": "autodata(type='float',length=(3,17)),autodata(type='float',length=(3,17))",
        "gps_city": "杭州市",
        "gps_province": "浙江省",
        "ov": "autodata(type='int',length=(3,10))",
        "regtime": "autodate('2014-01-11',0,datetype='day',flag='regtime')",
        "deviceNo": "autodata(type='int',length=(8,32))",
        "education":"大学本科",
        "job_type":"autodata(type='chinse',length=(0,20))",
        "pre_apply_no": "autodata(type='unique')",
        "source_channel": "Net_Sales_Pure_Online",
        "sub_source_channel": "51GJJ"
    },
    "gjj_brief": {
        "name": "公积金",
        "company": "autodata(type='chinese',length=(8,32))",
        "ID": "autodata(type='idcard')",
        "location_all": "杭州公积金中心",
        "city": "杭州",
        "state": "autodata(type='sample',samples=['正常','缴存'])",
        "base": "autodata(type='int',length=(1,4))",
        "balance": "autodata(type='int',length=(0,6))",
        "person_rate": "autodata(type='int',length=(0,2))",
        "company_rate": "autodata(type='all',length=(0,2))",
        "deposit_base": "autodata(type='int',length=(0,6))",
        "record_date": "autodate('2014-01-11',0,datetype='month')",
        "refresh_time": "autodata(type='int',length=(10,11))"
    },
    "gjj_detail": [
        {
          "company": "autodata(type='all',length=(8,32))",
          "record_date": "autodate('2014-01-11',-1,datetype='month',flag='gjj')",
          "op_type": "汇缴",
          "record_month": "autodate('2014-01-11',-1,datetype='month',outformat='%Y%m',flag='gjj_rm')",
          "amount": "autodata(type='int',length=(3,12))",
          "balance": "autodata(type='int',length=(3,12))"
        },20
    ],
    "loan_brief": {
        "con_no": "Cautodata(type='int',length=(10,12))",
        "state": "autodata(type='int',length=1)",
        "credit": "autodata(type='int',length=(0,12))",
        "period": "autodata(type='int',length=(1,2))",
        "rate": "autodata(type='int',length=(1,2))",
        "warn_rate": "autodata(type='int',length=(1,2))",
        "balance": "autodata(type='int',length=(1,2))",
        "fund": "autodata(type='int',length=(1,2))",
        "fund_date": "autodate('2014-01-11',0,datetype='month',outformat='%Y-%m-%d',flag='start')",
        "bank": "autodata(type='int',length=(1,2))",
        "phone": "autodata(type='int',length=(1,2))",
        "address": "autodata(type='int',length=(1,2))",
        "start_date": "autodate('2014-01-11',0,datetype='month',outformat='%Y-%m-%d',flag='start')",
        "end_date": "autodate('2014-01-11',0,datetype='month',outformat='%Y-%m-%d',flag='end')",
        "record_date": "autodate('2014-01-11',0,datetype='month',outformat='%Y-%m-%d',flag='record')",
        "refresh_time": "autodata(type='int',length=(1,2))"
    },
    "loan_detail": [
        {
            "record_date": "autodate('2014-01-11',-1,datetype='month',outformat='%Y-%m-%d',flag='loan_record')",
            "op_type": "autodata(type='int',length=(1,2))",
            "record_month": "autodata(type='int',length=(1,2))",
            "principle": "autodata(type='int',length=(1,2))",
            "interest": "autodata(type='int',length=(1,2))",
            "base": "autodata(type='int',length=(1,2))",
            "balance": "autodata(type='int',length=(1,2))",
            "bill_date": "autodate('2014-01-11',-1,datetype='month',outformat='%Y-%m-%d',flag='bill_date')"
        },10
    ],
    "call_brief": {
        "name": "autodata(type='name',length=(1,5))",
        "ID": "autodata(type='idcard')",
        "phone": "autodata(type='phone')",
        "center": "autodata(type='all',length=(0,10))",
        "time": "2016-09-22 19:08:27"
    },
    "call_detail": [
        {
          "start_time": "autodate('2014-01-11 00:00:00',-1,datetype='day',flag='call_detail_start_time')",
          "use_time": "0autodata(type='int',length=1):0autodata(type='int',length=1):1autodata(type='int',length=1)",
          "call_state": "autodata(type='sample',samples=['本地','外地'])",
          "call_type": "autodata(type='sample',samples=['主叫','被叫'])",
          "the_other": "autodata(type='phone')",
          "self_place": "杭州"
        },140
    ]
}
"""

mail_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>notice</title>
</head>
<body>
<div>您关注的分类<code style="color:red">{{ category }}</code>有新的{% if edit %}更新：{% else %}链接分享：{% endif %}</div>
<hr>
<div>标题: {{ title }}</div>
<div>链接: {{ link }}</div>
{% if desc %}<div>描述: {{ desc }}</div>{% endif %}
<div>{% if edit %}更新{% else %}创建{% endif %}人: {{ creator }}</div>
<hr>
点击查看分类下其他分享链接：{{ category_link }}
</body>
</html>"""
