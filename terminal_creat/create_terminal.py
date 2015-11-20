#-*- coding: UTF-8 -*-

# 批量创建终端设备号，符合E栈设备号生产规则
# 已应用于网盒迁移，可复用于其他需要批量生成设备号的场景

import MySQLdb
import csv
import sys
import os
reload(sys)
import re

sys.setdefaultencoding("utf-8")

fail_terminal = []
total_process = 0
created_terminal = []
# 读入文件，每行一个站点，提供E栈名称，所属区域，具体地址，缩略地址共四个字段，以逗号分隔。其中具体地址需要以XXX区开头以做正则匹配，如下例子：
# 东方欣悦居,福田,福田区福民路东方欣悦居欣悦阁大堂,东方欣悦居欣悦阁大堂
# 宏轩大厦,保税区,福田区石厦北宏轩大厦大堂入口,石厦北宏轩大厦大堂入口
FILEPATH_READ = "C:\\terminals_final2.csv"

# 输出文件，输出生成的设备编码
FILEPATH_WRITE = "C:\\with_terminalNo.csv"
TESTDB = ("", "root", "ROOT", "zj")

sql_get_zipcode = """ select zip from ez_department where department_name like "%s%%" order by zip"""
sql_get_area = """ select department_id,ids,area_id, zip from ez_department where department_name like "%s%%" order by zip """
sql_get_area_zh = """ select ta.name from t_base_area as ta where ta.code in (%s) """

sql_get_max = """select SUBSTRING(ez_terminal.terminal_no,8,2) from ez_terminal where terminal_no like "%%%s%%" and SUBSTRING(ez_terminal.terminal_no,8,2) = (select max(SUBSTRING(ez_terminal.terminal_no,8,2)) from ez_terminal where terminal_no like "%%%s%%" order by SUBSTRING(ez_terminal.terminal_no,8,2))"""
sql_insert_terminal = """ insert into ez_terminal (terminal_no,terminal_name,terminal_type,supplier_id,desk_id,mac_addr,department_id,department_ids,area_id,zips,area_name,loc_type,Location,status,remark,creater,updater,create_date,update_date,longitude,latitude,box_num,soft_version,heartbeat_status,use_date,en_box_num) values ("%s","%s","网盒临时柜型","18",null,null,"%s","%s","%s","%s","%s","A" ,"%s","0" ,"网盒批量生成",null,null,null,null,"","","",null,null,null,"")"""

db = MySQLdb.connect(*TESTDB, charset="utf8")
cursor = db.cursor()

def gen_terminal_id(temp_id):
    a = list(temp_id)
    sum_value = 0
    i = 0
    for b in a:
        pows = pow(2, i)
        if b >= "0" and b <= "9":
            sum_value += int(b) * pows
        elif b == "A":
            sum_value += 11 * pows
        elif b == "N":
            sum_value += 24 * pows
        i += 1
    print str(sum_value)[-1:]
    return str(sum_value)[-1:]

# 获取E栈邮编
def get_zip_code(district):
    result = cursor.execute(sql_get_zipcode % district)
    if result == 1:
        return cursor.fetchone()[0]
    else:
        return False

# 编码生产逻辑，参考mng应用的ID生产代码

def get_terminal_No(zip_code):
    zip_code_loc = zip_code+"A"
    print zip_code_loc
    print sql_get_max % (zip_code_loc, zip_code_loc)
    resultnum = cursor.execute(sql_get_max % (zip_code_loc, zip_code_loc))
    default_id = 0

    if resultnum == 1 or resultnum == 0:
        if resultnum == 1:
            maxid = int(cursor.fetchone()[0])
        else:
            maxid = 0

        if maxid < 50:
            maxid = 50
        maxid += 1
        zip_code_str = zip_code+"A"
        if maxid > 99:
            zip_code_loc = zip_code+"N"
            resultnum = cursor.execute(sql_get_max % (zip_code_loc, zip_code_loc))
            if resultnum == 1 or resultnum == 0:
                if resultnum == 1:
                    maxid = int(cursor.fetchone()[0])
                else:
                    maxid = 0
                maxid += 1
                zip_code_str = zip_code+"N"
            else:
                print ("Error in 2")
                return False
    else:
        print ("Error in 1")
        return False

    if maxid < 10:
        id_str = zip_code_str + "0" + str(maxid)
    else:
        id_str = zip_code_str + str(maxid)

    terminal_id_new = gen_terminal_id(id_str)
    print id_str + str(terminal_id_new)
    return id_str + str(terminal_id_new)

def create_terminal(_terminal_no, _terminal_name, _terminal_district, _terminal_loc, _loc_district):

    result_num = cursor.execute(sql_get_area % _loc_district)
    if result_num == 1:
        area = cursor.fetchone()
    else:
        print ("Wrong Area")
        return False
    department_id = area[0]
    ids = area[1]
    area_id = area[2]
    _zip = area[3]
    department_idss = "," + str(ids) + "," + str(department_id) + ","

    cursor.execute(sql_get_area_zh % (",".join(area_id.split(","))))
    area_zhs = cursor.fetchall()
    area_zh_str = ""
    for area_zh in area_zhs:
        area_zh_str = area_zh_str + area_zh[0]
    try:
        print sql_insert_terminal % (_terminal_no,_terminal_name, department_id, department_idss, area_id,
                                           _zip,area_zh_str, _terminal_loc)
        cursor.execute(sql_insert_terminal % (_terminal_no,_terminal_name, department_id, department_idss, area_id,
                                           _zip,area_zh_str, _terminal_loc))
        db.commit()
    except:
        print ("Could not creat temrinal %s for %s" % (_terminal_no, _terminal_name))
        return False
    return True

if __name__ == '__main__':

    with open(FILEPATH_READ) as csvfile_read:
        terminals = csv.reader(csvfile_read, delimiter=',')

        with open(FILEPATH_WRITE, 'w') as csvfile_write:
            terminals_with_No = csv.writer(csvfile_write, quoting=csv.QUOTE_MINIMAL)

            for terminal in terminals:
                total_process += 1
                # 中文编码
                terminal_name = ''.join(terminal[0].decode("gb2312"))
                terminal_district = ''.join(terminal[1].decode("gb2312"))
                terminal_loc = ''.join(terminal[2].decode("gb2312"))
                terminal_loc_short = ''.join(terminal[3].decode("gb2312"))
                print terminal_loc, terminal_loc_short

                # \u533a为“区”，因ez_department的department_name为xxx区XXX街道，需要重新组合字符以做查找
                loc_district = "深圳市"+re.match(ur'.*?\u533a', terminal_loc).group(0)+terminal_district
                print loc_district

                print terminal_name, terminal_district, loc_district

                zip_code = get_zip_code(loc_district)
                if zip_code:
                    terminal_no = get_terminal_No(zip_code)
                    print "terminal_no for %s is %s" % (terminal_name, terminal_no)
                else:
                    print "Wrong Zip code for %s" % terminal_name
                    fail_terminal.append(terminal_name)
                    continue

                if terminal_no:
                    if create_terminal(terminal_no, terminal_name, terminal_district, terminal_loc_short, loc_district):
                        print "Created for terminal_no %s, terminal_name %s " % (terminal_no, terminal_name)
                        created_terminal.append(terminal_name)
                    else:
                        terminal_no = "0"

                terminals_with_No.writerow(["%s,%s,%s,%s" % (terminal_name, terminal_district, terminal_loc_short, terminal_no)])

    print "total processed = %s, Fail = %s,  Created = %s" % (total_process, len(fail_terminal), len(created_terminal))
    print " ******Fail******* "
    print ",".join(fail_terminal)
    print " ******Created******** "
    print ",".join(created_terminal)
