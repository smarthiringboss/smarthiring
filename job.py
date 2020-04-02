import requests
import json
import os
import pymysql
from datetime import datetime
import time

import fetch

db = pymysql.connect (host="localhost", user="smarthiring",
                          password="Startnewlife2008", db="smart_hiring", port=3306)


def query_all_cookies():
    cookies = {
        "cookies" : [ ]
    }
    sql = "select cookie,mail from cookies;"
    try :
        cur = db.cursor ()
        cur.execute (sql)  # 执行sql语句

        results = cur.fetchall ()  # 获取查询的所有记录
        print ("cookie", "mail")
        # 遍历结果
        for row in results :
            cookie = {
                "cookie" : row [ 0 ],
                "mail" : row [ 1 ]
            }
            cookies [ "cookies" ].append (cookie)

            # print (cookie)
    except Exception as e :
        print (e)
        # raise e
    finally :
        # db.close ()  # 关闭连接
        print ("查询cookie结束")

    return cookies

def fetch_geeks(cookie, mail):

    cookie_dict = fetch.convert_cookie(cookie)
    for i in range(1,10):
        time.sleep (10)
        result, logPath = fetch.get_geeks(cookie_dict,i)
        if "fail" == result:
            print("返回不正确，退出。。。")
            # return {"result":"fail","logPath":"../reports/" + logPath.split("/")[3]}
            return
        fetch.extrat_geeks(result)

    # return {"result":"pass","logPath":"../reports/" + logPath.split("/")[3]}
    return

def job():
    cookies = query_all_cookies()
    for cookie in cookies["cookies"]:
        fetch_geeks (cookie["cookie"], cookie["mail"])

# 每n秒执行一次
def timer(n):
    while True:
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        job()
        time.sleep(n)
# 5s
timer(1800)