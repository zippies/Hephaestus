# -*- coding: utf-8 -*-
from multiprocessing.dummy import Pool as ThreadPool
from threading import Thread
import requests, re, os
import sys, time
import random
reload(sys)
sys.setdefaultencoding("utf-8")

source_list = []
ready_dirs = []
regx_str = "/packages/(\w+/?[-.\w\d]+[.tar.gz|.whl|.zip|.tar.bz2])"
base_url = "http://pypi.pediapress.com/packages/"
cmd_mkdir = "mkdir -p %s"
cmd_download = "cd %s&&wget %s"
finish = []

print "正在解析..."
begin = time.time()
resp = requests.get(base_url)

if resp.status_code == 200:
    for item in re.finditer(regx_str, resp.text):
        match_str = item.groups()[0]
        if "/" not in match_str:
            source_list.append((base_url + match_str, "."))
        else:
            package = match_str.split("/")[0]

            if package not in ready_dirs:
                os.system(cmd_mkdir %package)
                ready_dirs.append(package)

            source_list.append((base_url + match_str, package))
end = time.time()

print "初始化解析，用时:%.1f秒" % (end - begin)

def countFinish():
    while True:
        print len(finish)
        time.sleep(5)


def download(item):
    time.sleep(random.randint(1,3))
    link, package_path = item
    try:
        r = requests.get(link, timeout=(20,120))
        if r.status_code == 200:
            with open(os.path.join(package_path, link.split("/")[-1]), "wb") as f:
                f.write(r.content)
            finish.append(1)
        else:
            print "下载失败:", link, r.status_code, r.reason
    except Exception as e:
        print "下载失败:", link, str(e)


if __name__ == "__main__":
    t = Thread(target=countFinish)
    t.setDaemon(True)
    t.start()

    pool = ThreadPool(3)
    pool.map(download, source_list[2429:])
