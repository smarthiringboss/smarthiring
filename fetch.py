import requests
import json
import os
import pymysql
import datetime
import time

db = pymysql.connect (host="localhost", user="smarthiring",
                      password="Startnewlife2008", db="smart_hiring", port=3306)


def convert_cookie(cookie) :
    # kname = open ('cookie.txt', "r")
    # cookie = kname.read()

    cookie_dict = {i.split ("=") [ 0 ] : i.split ("=") [ -1 ] for i in cookie.split ("; ")}

    return cookie_dict


def get_geeks(cookie_dict, page) :
    print ("取第" + str (page) + "页")

    filename = str (time.time ())
    # 日志文件，和reports放在一起
    logfile = open ('../ice_smarthire/reports/log_{0}.yml'.format (filename), "w")

    # 当前时间
    current_milli_time = int (round (time.time () * 1000))

    headers = {
        "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36",
    }
    # todo: 暂未设置jobid
    response = requests.get (
        "https://www.zhipin.com/wapi/zprelation/interaction/bossGetGeek?jobid=-1&status=1&refresh=" + str (
            current_milli_time) + "&source=0&switchJobFrequency=-1&salary=0&age=16,-1&school=-1&major=0&exchangeResumeWithColleague=0&degree=0&experience=0&intention=-1&page=" + str (
            page) + "&jobId=-1&tag=1&_=" + str (current_milli_time),
        headers=headers, cookies=cookie_dict)

    try :
        geeks = json.loads (response.text)
        logfile.write (str (geeks))
    except Exception as e :
        print (e)
        logfile.write (response.text)
        return "fail", logfile.name
    finally :
        logfile.close ()

    if "code" in geeks:
        if geeks["code"] != 0 :
            print("boss return with wrong code ")
            print ("the cookie is :" + cookie_dict)
            return "fail", logfile.name
    elif "message" in geeks:
        if geeks["message"] == "Forbidden" :
            print("boss return with Forbidden "
            print("the cookie is :"+cookie_dict)
            return "fail", logfile.name

    return geeks [ "zpData" ] [ "geekList" ], logfile.name


def insert_geek(geekId, geekName, geekGender, geekWorkYear, geekDegree, geekDesc, salary, middleContent, actionDateDesc,
                actionDate, school, major, degreeName, expectLocation, activeSec, expectLocationName,
                expectPositionName, ageDesc, company, positionName) :
    # 最近活跃时间 - 秒
    activeSec = datetime.datetime.fromtimestamp (activeSec)
    activeSec = activeSec.strftime ("%Y-%m-%d %H:%M:%S")
    # 注册账号时间 - 毫秒
    actionDate = datetime.datetime.fromtimestamp (actionDate / 1000)
    actionDate = actionDate.strftime ("%Y-%m-%d %H:%M:%S")

    # 使用cursor()方法获取操作游标
    cur = db.cursor ()

    sql_insert = """insert into geeks(id, geekId, geekName,geekGender,geekWorkYear,geekDegree,geekDesc, salary,middleContent,actionDateDesc,actionDate,school,major,degreeName,expectLocation,activeSec,expectLocationName,expectPositionName,ageDesc,company,positionName) values(""" + str (
        geekId) + """, """ + str (geekId) + """, '""" + geekName + """',""" + str (
        geekGender) + """,'""" + geekWorkYear + """','""" + geekDegree + """','""" + geekDesc + """', '""" + salary + """','""" + middleContent + """','""" + actionDateDesc + """','""" + actionDate + """','""" + school + """','""" + major + """','""" + degreeName + """',""" + str (
        expectLocation) + """,'""" + activeSec + """','""" + expectLocationName + """','""" + expectPositionName + """','""" + ageDesc + """','""" + str (
        company).replace ("'", "") + """','""" + str (positionName).replace ("'", "") + """')"""

    try :
        cur.execute (sql_insert)
        # 提交
        db.commit ()
    except Exception as e :
        # 错误回滚
        print (e)
        db.rollback ()
    finally :
        print ("插入" + geekName)
        # db.close ()


def extrat_geeks(geeks) :
    for geek in geeks :
        geekId = geek [ "geekCard" ] [ "geekId" ]
        geekName = geek [ "geekCard" ] [ "geekName" ]
        geekGender = geek [ "geekCard" ] [ "geekGender" ]
        geekWorkYear = geek [ "geekCard" ] [ "geekWorkYear" ]
        geekDegree = geek [ "geekCard" ] [ "geekDegree" ]
        geekDesc = geek [ "geekCard" ] [ "geekDesc" ] [ "content" ]
        salary = geek [ "geekCard" ] [ "salary" ]
        middleContent = geek [ "geekCard" ] [ "middleContent" ] [ "content" ]
        actionDateDesc = geek [ "geekCard" ] [ "actionDateDesc" ]
        actionDate = geek [ "geekCard" ] [ "actionDate" ]
        school = geek [ "geekCard" ] [ "geekEdu" ] [ "school" ]
        major = geek [ "geekCard" ] [ "geekEdu" ] [ "major" ]
        degreeName = geek [ "geekCard" ] [ "geekEdu" ] [ "degreeName" ]
        expectLocation = geek [ "geekCard" ] [ "expectLocation" ]
        activeSec = geek [ "geekCard" ] [ "activeSec" ]
        expectLocationName = geek [ "geekCard" ] [ "expectLocationName" ]
        expectPositionName = geek [ "geekCard" ] [ "expectPositionName" ]
        ageDesc = geek [ "geekCard" ] [ "ageDesc" ]
        others = {
            "company" : [ ],
            "positionName" : [ ]
        }
        for geekWork in geek [ "geekCard" ] [ "geekWorks" ] :
            others [ "company" ].append (geekWork [ "company" ])
            others [ "positionName" ].append (geekWork [ "positionName" ])

        insert_geek (geekId, geekName, geekGender, geekWorkYear, geekDegree, geekDesc, salary, middleContent,
                     actionDateDesc, actionDate, school, major, degreeName, expectLocation, activeSec,
                     expectLocationName, expectPositionName, ageDesc, others [ "company" ], others [ "positionName" ])


def query_if_cookie_exist(mail) :
    sql = "select * from cookies where mail='" + mail + "';"
    try :
        cur = db.cursor ()
        cur.execute (sql)  # 执行sql语句

        results = cur.fetchall ()  # 获取查询的所有记录
        print ("cookie", "mail")
        # 遍历结果
        for row in results :
            # cookie = row [ 1 ]
            # print (cookie)
            return True
    except Exception as e :
        print (e)
        # raise e
    finally :
        # db.close ()  # 关闭连接
        print ("查询cookie结束")

    return False


def update_cookie(cookie, mail, valid) :
    ifExist = query_if_cookie_exist (mail)

    # 插入
    if not ifExist :
        cur = db.cursor ()

        sql_insert = """insert into cookies(valid, mail, cookie) values(""" + str(valid) + """,'""" + mail + """','""" + cookie + """')"""
        try :
            cur.execute (sql_insert)
            # 提交
            db.commit ()
        except Exception as e :
            # 错误回滚
            print (e)
            db.rollback ()
        finally :
            print ("插入cookie for " + mail)
            # db.close ()
    # 更新
    else :
        cur = db.cursor ()

        sql_insert = """update cookies set valid=""" + str(valid) + """,cookie='""" + cookie + """' where mail='""" + mail + """'"""
        try :
            cur.execute (sql_insert)
            # 提交
            db.commit ()
        except Exception as e :
            # 错误回滚
            print (e)
            db.rollback ()
        finally :
            print ("更新cookie for " + mail)
            # db.close ()


def fetch_geeks(cookie, mail) :
    # 先保存再执行
    update_cookie (cookie, mail, 1)
    # return
    cookie_dict = convert_cookie (cookie)
    # for i in range(1,1):
    result, logPath = get_geeks (cookie_dict, 1)
    if "fail" == result :
        print ("返回不正确，退出。。。")
        return {"result" : "fail", "logPath" : "../reports/" + logPath.split ("/") [ 3 ]}
    extrat_geeks (result)


    print ("extract 结束，准备返回")
    returnString = {"result" : "pass", "logPath" : "../reports/" + logPath.split ("/") [ 3 ]}
    return returnString
