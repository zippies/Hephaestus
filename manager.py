# -*- coding: utf-8 -*-
from app import createApp
from flask import render_template
from app.models import db, Tool
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from werkzeug.contrib.fixers import ProxyFix
import sys,os
reload(sys)
sys.setdefaultencoding('utf-8')

app = createApp()
app.wsgi_app = ProxyFix(app.wsgi_app)
manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)


@manager.command
def dbinit():
    db.create_all()
    print 'dbinit ok'


@manager.command
def dbdrop():
    db.drop_all()
    print 'ok'


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404


if __name__ == '__main__':
    if not os.path.exists("data.sqlite") and sys.argv[1] == "runserver":
        print("[error]数据库尚未初始化，请先运行:python manager.py dbinit")
    else:
        manager.run()