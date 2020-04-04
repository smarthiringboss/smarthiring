import requests
import json
import os
import pymysql
from datetime import datetime
import time

import fetch
import mail

db = pymysql.connect (host="localhost", user="smarthiring",
                          password="Startnewlife2008", db="smart_hiring", port=3306)


def query_valid_cookies():
    cookies = {
        "cookies" : [ ]
    }
    sql = "select cookie,mail from cookies where valid=1;"
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


def fetch_geeks(cookie, mail_address):

    cookie_dict = fetch.convert_cookie(cookie)
    for i in range(1,100):
        # 调节每页查询间隔
        time.sleep (30)

        result, logPath = fetch.get_geeks(cookie_dict,i)
        if "fail" == result:
            print(mail_address+"的返回不正确，通知mail发送。。。")

            # 把这个cookie无效掉
            fetch.update_cookie (cookie, mail_address, 0)

            mailto_list = [mail_address, '13732164@qq.com']
            for mailto in mailto_list:
                # 发送mail通知
                print("mail通知"+mailto)
                mail.send_mail ( \
                           receiver=mailto, mail_title=mail_address+'的cookie已过期', \
                           mail_content='')

            return

        fetch.extrat_geeks(result)

    return

def job():
    cookies = query_valid_cookies()
    for cookie in cookies["cookies"]:
        fetch_geeks (cookie["cookie"], cookie["mail"])

# 每n秒执行一次
def timer(n):
    while True:
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        job()
        time.sleep(n)
# 5s
timer(43200)