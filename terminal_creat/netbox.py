#-*- coding: UTF-8 -*-
__author__ = '01348930'

#
# 网盒设备柜型转换为E栈柜型
#
# 输入文件netbox.csv，格式为网盒站点编号，设备大类，如下所示：
# 800459,IPC
# 800534,QT

import MySQLdb

import csv

FILEPATH_READ = "C:\\netbox.csv"
FILEPATH_WRITE = "C:\\netbox_withType.csv"

# 网盒数据库
TESTDB = ("", "root", "", "")
type_list = {}
numtype = {'a': 0}

getTypeSQL = """select site_id,cabinet_type,cabinet_id from ns_box as ta where site_id = "%s" group by ta.site_id, ta.cabinet_type, cabinet_id"""


if __name__ == '__main__':

    db = MySQLdb.connect(*TESTDB, charset="utf8", port=22580)
    cursor = db.cursor()

    with open(FILEPATH_READ) as csvfile_read:
        terminals = csv.reader(csvfile_read, delimiter=',')
        with open(FILEPATH_WRITE, 'w') as csvfile_write:
            terminals_with_type = csv.writer(csvfile_write, quoting=csv.QUOTE_MINIMAL)

            for terminal in terminals:
                terminal_id = terminal[0]
                terminal_type = terminal[1]
                print terminal_id, terminal_type

                cursor.execute(getTypeSQL % terminal_id)

                t_types = cursor.fetchall()
                type_list[terminal_id] = []

                # 具体转换规则，根据实际业务而定
                for t_type in t_types:
                    print t_type[1]
                    if terminal_type == "IPC":
                        if t_type[1] in ("cType9000", "cType6001"):
                            type_list[terminal_id].append(t_type[1]+"COM-Main-Left")

                            if t_type[1]+"COM-Main-Left" not in numtype.keys():
                                numtype[t_type[1]+"COM-Main-Left"] = 1
                            else:
                                numtype[t_type[1]+"COM-Main-Left"] += 1

                            type_list[terminal_id].append(t_type[1]+"COM-Main-Right")

                            if t_type[1]+"COM-Main-Right" not in numtype.keys():
                                numtype[t_type[1]+"COM-Main-Right"] = 1
                            else:
                                numtype[t_type[1]+"COM-Main-Right"] += 1

                        elif t_type[1] in ("cType9001", "cType6002"):
                            type_list[terminal_id].append(t_type[1]+"COM-Belong")
                            type_list[terminal_id].append(t_type[1]+"COM-Belong")
                            if t_type[1]+"COM-Belong" not in numtype.keys():
                                numtype[t_type[1]+"COM-Belong"] = 2
                            else:
                                numtype[t_type[1]+"COM-Belong"] += 2

                    elif terminal_type == "QT":
                        if t_type[1] in ("cType9000", "cType6001"):
                            type_list[terminal_id].append(t_type[1]+"IP-Main")
                            if t_type[1]+"IP-Main" not in numtype.keys():
                                numtype[t_type[1]+"IP-Main"] = 1
                            else:
                                numtype[t_type[1]+"IP-Main"] += 1
                        elif t_type[1] in ("cType9001", "cType6002"):
                            type_list[terminal_id].append(t_type[1]+"IP-Belong")
                            if t_type[1]+"IP-Belong" not in numtype.keys():
                                numtype[t_type[1]+"IP-Belong"] = 1
                            else:
                                numtype[t_type[1]+"IP-Belong"] += 1
                print(type_list[terminal_id])
                terminals_with_type.writerow(["%s,%s, %s" % (terminal_id, terminal_type, ",".join(type_list[terminal_id]))])

    for k, v in numtype.items():
        print k, v

    db.close()















