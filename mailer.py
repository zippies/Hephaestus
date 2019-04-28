# -*- coding: utf-8 -*-
from celery import Celery
from email.header import Header
from email.mime.text import MIMEText
from jinja2 import Template
from config import mail_template
from config import Config
from lib.methods import decrypt
import smtplib
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

#BROKER_URL = 'mongodb://localhost:27017/database_name'

app = Celery("emailer", broker=Config.BROKER_URL)


@app.task
def anydoor_notice(category, title, link, desc, creator, category_link, tolist, edit=False):
    content = Template(mail_template).render(
        category=category,
        title=title,
        link=link,
        desc=desc,
        creator=creator,
        category_link=category_link,
        edit=edit
    )

    msg = MIMEText(content, 'html', 'utf-8')
    msg['Subject'] = Header(u'任意门', 'utf-8').encode()
    server = smtplib.SMTP("mail.company.com", 25)
    server.set_debuglevel(1)
    server.login(decrypt("MFSCARWDNKE\"YCECKEQO"), decrypt("%JWSKCPU"))
    server.sendmail(decrypt("MFSCARWDNKE\"YCECKEQO"), tolist, msg.as_string())
    # server.quit()





