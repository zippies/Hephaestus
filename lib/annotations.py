#coding:utf-8
import time
from methods import *

def AutoData(count=None,index=None):
    def _gendata(func):
        def _deco(self,*args,**kwargs):
            self._tmp_doc_ = func.__doc__
            allpass = True
            errors = []
            sample = self.dataTemplate if hasattr(self,"dataTemplate") else self.data
            datas = deallist(sample)
            sampleStr = js.dumps(datas)
            datas = genData(sampleStr,count)
            if count or index:
                if index and index < len(datas):
                    #如果指明了需要某个下标的数据，则返回该数据
                    datas = [datas[index]]
                else:
                    datas = datas[:count]
            if count > 1:
                print(u"测试数据量:%s" %len(datas))
            for i,data in enumerate(datas):
                if count > 1:
                    print "-"* 35 + "测试数据:%s"%(i+1) + "-"*35
                self.data = data
                try:
                    self.logger.log("-"*35,"测试数据:%s"%(i+1),"-"*35)
                    start = time.time()
                    func(self,*args,**kwargs)
                    end = time.time()
                    if count > 1:
                        print(" 测试结果: pass 用时:%ss" %round(end-start,3))
                except Exception as e:
                    allpass = False
                    errors.append(str(e))
                    if count > 1:
                        print " 测试结果: fail  [errorMsg]:%s" %e

            if not allpass:
                raise Exception("|".join(list(set(errors))))

        return _deco
    return _gendata

def RunCount(count=None):
    def _deco(func):
        def _func(self):
            print(func.__doc__)
            ispass = True
            errors = []
            for i in range(count):
                print(u"第%s次循环" %str(i+1))
                try:
                    func()
                except:
                    errors.append(i+1)
                    ispass = False

            raise Exception(u"第%s次循环失败")
        return _func

    return _deco

def Data(file=None):
    def _deco(func):
        def _func(self):
            print(func.__doc__)
            if file.endswith(".txt"):
                with open(file,'r') as f:
                    lines = [line.strip() for line in f.readlines() if line.strip()]
                    self.datas = [line.split("||") for line in lines]
            elif file.endswith(".excel"):
                pass

            print(u"测试数据量:%s" %len(self.datas))
            for data in self.datas:
                func(self,[d.strip() for d in data])

        return _func
    return _deco

def WaitAutoCredit(applyCode_key,taskname="初审",timeout=600,interval=5,needupdate=True):
    def _gendata(func):
        def _deco(self):
            starttime = time.time()
            sleep(10)
            self._tmp_doc_ = func.__doc__
            applyCode = getenv(applyCode_key)

            while time.time() - starttime < timeout:
                db_taskname = self.db.execute(
                    "select task_name from newapp.workflow_curr_task where apply_code='%s'" % applyCode)
                if db_taskname[0][0] == "拒绝结束":
                    raise Exception("申请件被拒绝，退出")
                if db_taskname[0][0] == taskname:
                    break
                else:
                    print "not yet complete:%s taskname:%s" % (applyCode,db_taskname[0][0])
                    if needupdate:
                        self.db.execute("update newapp.job_detail set status='BIZ_SUCCESS' where apply_code='%s'" % applyCode)
                sleep(interval)
            else:
                raise Exception("申请件:%s 等待到:%s 超时(timeout=%s秒)" %(applyCode,taskname,timeout))
            print "autocredit01 complete 用时:%s秒" %(round(time.time()-starttime,2))
            func(self)

        return _deco

    return _gendata
