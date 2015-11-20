# -*- coding: UTF-8 -*-

#
# 根据生产短信追加营销短信
#

import httplib
import logging
import sys
import urllib
reload(sys)
import time
import MySQLdb
import datetime
import traceback
sys.setdefaultencoding("utf-8")

sql_sms_target = """ select DISTINCT mobile from t_base_sms_history as ta,ez_parcel as tb,zj.ez_terminal as tc where ta.biz_type = "take.open.key" and ta.create_date >= str_to_date("%s","%%Y-%%m-%%d %%H:%%i:%%s") and ta.create_date < str_to_date("%s","%%Y-%%m-%%d %%H:%%i:%%s") and ta.biz_id = tb.id and tb.terminal_no = tc.terminal_no and tc.area_name like "%%深圳%%" """

HOST = ""
PORT =
URL = "/MWGate/wmgw.asmx/MongateSendSubmit?"
MSG = "回复TD退订"
PASSWD = ''
USRID = ''
SUBPORT = '*'
MAXNUM = 90

# 定义扫描间隔
SCANINTERVAL = 60
# IP，port，账号，密码
TESTDB = ("", "", "", "")

logger = logging.getLogger("MarketSMSLogger")
logger.setLevel(logging.DEBUG)
logh = logging.FileHandler("./SMS_logger")
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logh.setFormatter(formatter)
logger.addHandler(logh)


class SMSutil():
    def __init__(self):
        self._httpconn = httplib.HTTPConnection(HOST, PORT, timeout=10)
        self.param = dict()
        # 短信平台接口账号密码
        self.param['userId'] = USRID
        self.param['password'] = PASSWD
        self.param['pszSubPort'] = SUBPORT
        self.param['pszMobis'] = []

        # 仅支持相同内容群发，消息内容请更新MSG变量
        self.param['pszMsg'] = MSG
        self.param['iMobiCount'] = 0

    # 发送函数，传入发送手机号，最多不超过100个
    def send_msg(self, target):
        self.param['pszMobis'] = target
        logger.info("Send Target is %s" % self.param['pszMobis'])
        self.param['iMobiCount'] = str(len(target.split(',')))
        logger.info("Send Count is %s" % self.param['iMobiCount'])
        request_url = urllib.urlencode(self.param)
        request_url = URL + request_url
        logger.info(request_url)
        self._httpconn.request("GET", request_url)
        r1 = self._httpconn.getresponse()
        logger.info(r1.status, r1.reason)
        logger.info(r1.read())

def connectDB():
    _db = None
    while not _db:
        try:
            _db = MySQLdb.connect(*TESTDB, charset="utf8")
            print "connected"
            return _db
        except:
            logger.error("unable to connect DB, Wait 5m and retry")
            time.sleep(300)


if __name__ == "__main__":

    smsUtil = SMSutil()
    last_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()-600))
    db = connectDB()
    while True:

        if not db:
            db = connectDB()
        cursor = db.cursor()
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        print sql_sms_target
        logger.info(sql_sms_target % (last_time, current_time))

        numofrecord = cursor.execute(sql_sms_target % (last_time, current_time))
        logger.info("Record Number = %d " % numofrecord)
        if numofrecord > 0:
            phone_list = []
            targets = cursor.fetchmany(MAXNUM)
            while targets:
                for target in targets:
                    phone_list.append(target[0])

                phones = ",".join(phone_list)
                smsUtil.send_msg(phones)
                time.sleep(5)
                phone_list = []
                targets = cursor.fetchmany(MAXNUM)
        last_time = current_time
        db.commit()
        cursor.close()
        time.sleep(SCANINTERVAL)


