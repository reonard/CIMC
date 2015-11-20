# -*- coding: UTF-8 -*-
__author__ = '01348930'

#
# 营销短信发送程序
#

import httplib
import sys
import csv
import urllib
reload(sys)
import time
sys.setdefaultencoding("utf-8")

# 发送平台的ip端口
HOST = ""
PORT =
# 发送平台接口
URL = "/MWGate/wmgw.asmx/MongateSendSubmit?"
MSG = """短信发送内容。回复TD退订"""
# 填入发送平台的账号密码
PASSWD = ''
USRID = ''
# SUBPORT星号即可，无须更改
SUBPORT = '*'
# 发送手机号文件，每行一个手机号，以分号结尾
# eg：
# 18665880123，
# 18992330412，
TARGET_FILE = "C:\sms.csv"
MAXNUM = 90


class SMSutil():
    def __init__(self):
        self._httpconn = httplib.HTTPConnection(HOST, PORT, timeout=10)
        self.param = dict()
        self.param['userId'] = USRID
        self.param['password'] = PASSWD
        self.param['pszSubPort'] = SUBPORT
        self.param['pszMobis'] = []
        self.param['pszMsg'] = MSG
        self.param['iMobiCount'] = 0

# 发送函数，传入发送手机号，最多不超过100个
    def send_msg(self, target):

        self.param['pszMobis'] = target
        print self.param['pszMobis']
        self.param['iMobiCount'] = str(len(target.split(',')))

        request_url = urllib.urlencode(self.param)
        request_url = URL + request_url
        print request_url
        self._httpconn.request("GET", request_url)
        r1 = self._httpconn.getresponse()
        print (r1.status, r1.reason)
        print r1.read()
        self._httpconn.close()

if __name__ == "__main__":
    smsUtil = SMSutil()
    phone_nums = []
    read_num = 0
    with open(TARGET_FILE) as csvfile:
        regInfos = csv.reader(csvfile, delimiter=',')
        for regInfo in regInfos:
            phone_nums.append(regInfo[0])
            read_num += 1
            if len(phone_nums) == MAXNUM:
                target = ",".join(phone_nums)
                smsUtil.send_msg(target)
                phone_nums = []
                time.sleep(10)

        if len(phone_nums) > 0:
            target = ",".join(phone_nums)
            smsUtil.send_msg(target)
        print read_num













