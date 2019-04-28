# encoding:utf-8
import requests
import os
import datetime
import time

tools_url = "http:///pipsource/latest"
cmd_pip = "cd ..&&pip download %s --trusted-host pypi.douban.com"
cmd_wget = "wget http:///static/downloads/%s"

def timenow():
    plus = datetime.timedelta(hours=8)
    sys_now = datetime.datetime.now()
    current = sys_now + plus
    return current.strftime("%Y-%m-%d %H:%M:%S")

while True:
    r = requests.get(tools_url)
    if r.status_code == 200:
        packages = r.json().get("packages")
        locals = r.json().get("locals")
        if packages:
            os.system(cmd_pip % " ".join(packages))
            print timenow(), "pip download ok", packages
        else:
            print timenow(), "no new packages found"
        if locals:
            for lp in locals:
                os.system(cmd_wget % lp)
                print timenow(), "wget ok", lp
        else:
            print timenow(), "no new user packages found"
    else:
        print timenow(), r.status_code, r.reason

    time.sleep(10)