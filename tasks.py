import os
import sys
import subprocess
import time
import json
import pymysql

db = pymysql.connect (host="localhost", user="smarthiring",
                          password="Startnewlife2008", db="smart_hiring", port=3306)

def DirAll(pathName, toggled) :
    children = {
        "name" : pathName,
        "children" : [ ]
    }
    if toggled :
        toggle = {"toggled" : "true"}
        children.update (toggle)

    if os.path.exists (pathName) :
        fileList = os.listdir (pathName)
        for f in fileList :
            if f == ".git" or f == "__pycache__" :
                continue;
            f = os.path.join (pathName, f)
            if os.path.isdir (f) :
                children [ "children" ].append (DirAll (f, False))
            else :
                dirName = os.path.dirname (f)
                baseName = os.path.basename (f)
                fileNode = {
                    "name" : baseName,
                    "fullPath" : f
                }
                children [ "children" ].append (fileNode)
                # print(f)
    return children


def get_all_files() :
    # data = {
    #     "name": 'root',
    #     "toggled": 'true',
    #     "children": []
    # }
    print ("获取目录: " + os.getcwd ())
    children = DirAll (os.getcwd (), True)
    return json.dumps (children)


def get_code(path) :
    testFile = open (path, "r")
    return testFile.read ()


def submit_code(path, codePiece) :
    isExists = os.path.exists (os.path.dirname (path))
    if not isExists :
        # 如果不存在则创建目录
        os.makedirs (os.path.dirname (path))
        print (path + ' 创建目录成功')

    # 写文件
    testFile = open (path, "w+")
    testFile.write (codePiece)
    return "{\"result\":\"pass\"}"


def fetch_testcases() :
    docList = os.listdir ('testcases/')  # 特定目录下的文件存入列表
    docList.sort ()  # 显示当前文件夹下所有文件并进行排序

    testcases = [ ]
    # 每个文件testcase读出来
    for file in docList :
        if not os.path.isdir ('testcases/' + file) :
            testcase = {
                "value" : file,
                "text" : file
            }
            testcases.append (testcase)

    return json.dumps (testcases)


def query_testcases(fileName) :
    jsonFile = open ("testcases/" + fileName, "r")
    return json.dumps (json.loads (jsonFile.read ()))


def convert_db_to_geek(row):
    geek = {
        "id" : row [ 0 ],
        "geekId" : row [ 1 ],
        "geekName" : row [ 2 ],
        "geekGender" : row [ 3 ],
        "geekWorkYear" : row [ 4 ],
        "geekDegree" : row [ 5 ],
        "geekDesc" : row [ 6 ],
        "salary" : row [ 7 ],
        "middleContent" : row [ 8 ],
        "actionDateDesc" : row [ 9 ],
        "actionDate" : row [ 10 ],
        "school" : row [ 11 ],
        "major" : row [ 12 ],
        "degreeName" : row [ 13 ],
        "expectLocation" : row [ 14 ],
        "activeSec" : row [ 15 ],
        "expectLocationName" : row [ 16 ],
        "expectPositionName" : row [ 17 ],
        "ageDesc" : row [ 18 ],
        "company" : row [ 19 ],
        "positionName" : row [ 20 ]
    }
    return geek

def fetch_tasks() :
    lanes = {
        "lanes" : [ ]
    }
    groups = [ ]

    # 统计总体分类
    sql = "select count(1),expectPositionName from geeks group by expectPositionName;"
    try :
        cur = db.cursor ()
        cur.execute (sql)  # 执行sql语句

        results = cur.fetchall ()  # 获取查询的所有记录
        print ("count", "expectPositionName")
        # 遍历结果
        for row in results :
            count = row [ 0 ]
            expectPositionName = row [ 1 ]
            print (count, expectPositionName)
            groups.append ({"count" : count, "expectPositionName" : expectPositionName})
    except Exception as e :
        print (e)
        raise e
    finally :
        # db.close ()  # 关闭连接
        print("查询分类结束")

    laneId = 0
    # 循环填充卡片
    for group in groups :
        lane = {
            "id" : laneId,
            "label" : '',
            "title" : group [ "expectPositionName" ],
            "style" : {"backgroundColor" : "#D3D3D3"},
            "cards" : [ ]
        }

        cur = db.cursor ()
        # 注册时间小于7天
        sql = "select * from geeks where expectPositionName='"+group [ "expectPositionName" ]+"' and TO_DAYS( NOW( ) ) - TO_DAYS( actionDate)<=7 order by actionDate desc;"
        try :
            cur.execute (sql)  # 执行sql语句

            results = cur.fetchall ()  # 获取查询的所有记录
            print ("id", "name")
            # 遍历结果
            for row in results :
                geek = convert_db_to_geek(row)
                print (geek["id"], geek["geekName"])
                card = {
                    "id" : geek["id"],
                    "title" : geek["geekName"]+" ("+geek["expectLocationName"]+", "+geek["geekWorkYear"]+", "+geek["salary"]+")",
                    "description" : "注册时间:"+str(geek["actionDate"])+"--"+geek["company"]+"--"+geek["positionName"],
                    "label" : geek["activeSec"].strftime("%m月%d日 %H点登陆"),
                    "content" : geek["geekName"]+"\n "+str(geek["geekGender"])+"\n "+geek["geekWorkYear"]+"\n "+geek["geekDegree"]+"\n "+geek["salary"]+"\n "+geek["middleContent"]+"\n "+geek["actionDateDesc"]+"\n 注册时间:"+str(geek["actionDate"])+"\n "+geek["school"]+"\n "+geek["major"]+"\n "+geek["degreeName"]+"\n "+str(geek["expectLocation"])+"\n 上次登录:"+str(geek["activeSec"])+"\n "+geek["expectLocationName"]+"\n "+geek["expectPositionName"]+"\n "+geek["ageDesc"]+"\n "+geek["company"]+"\n "+geek["positionName"]+"\n "+geek["geekDesc"]
                }
                lane [ "cards" ].append (card)

            lanes [ "lanes" ].append (lane)
            laneId += 1
        except Exception as e :
            print(e)
            raise e
        finally :
            # db.close ()  # 关闭连接
            print ("查询 "+group [ "expectPositionName" ]+" geeks结束")

    return json.dumps (lanes)


def save_tasks(params, laneId, fileName) :
    print (fileName)
    fname = open ('testcases/{0}.json'.format (fileName), "w")
    fname.write (json.dumps (params))
    fname.close ()
    returnString = "{\"result\":\"pass\"}"

    return returnString


def goto(params, mobile, laneId, host, debugOption) :
    # 取到对应lane id的泳道列表级
    for lane in params [ "lanes" ] :
        if lane [ "id" ] == laneId :
            tasks = lane [ "cards" ]

    args_debug = ""
    args_report = ' --report-dir ../ice/reports '

    if host == "localhost" :
        stripP = ""
    else :
        stripP = "\n"

    if debugOption == "debug" :
        args_debug = " --log-level debug"

    docList = os.listdir ('testcases/')  # 特定目录下的文件存入列表
    docList.sort ()  # 显示当前文件夹下所有文件并进行排序

    # 新建流程yml文件,临时文件，运行后会删除
    filename = str (time.time ())
    fname = open ('test_{0}.yml'.format (filename), "w")
    # 日志文件，和reports放在一起
    logfile = open ('../ice/reports/log_{0}.yml'.format (filename), "w")

    # 读入主配置
    configFile = open ('config.yml', "r")
    configNewFile = open ('config{0}.yml'.format (time.time ()), "w")

    # 暂时每次手机号加1确保不重复
    # todo: 丑陋的临时方案，后续会优化成统一生产唯一手机号
    newMobile = ""
    try :
        while True :
            text_line = configFile.readline ()
            if text_line :
                if text_line.find ("mobile:") != -1 :
                    # 如果传入手机号，则无需自增
                    if len (str (mobile)) != 11 :
                        newMobile = str (int (text_line.split (":") [ 1 ].replace ("\"", "")) + 1)
                        print ("此次手机号为：" + newMobile)
                        fname.writelines ("        mobile: \"" + newMobile + "\"\n")
                        configNewFile.writelines ("        mobile: \"" + newMobile + "\"\n")
                    else :
                        newMobile = mobile
                        print ("此次手机号为：" + newMobile)
                        fname.writelines ("        mobile: \"" + newMobile + "\"\n")
                        configNewFile.writelines (text_line)
                else :
                    fname.writelines (text_line)
                    configNewFile.writelines (text_line)
            else :
                break
    finally :
        # 通过秒级文件名确保不冲突
        # todo: 肯定不是线程安全的，但是目前版本基本不会出现同一秒两个人点击
        configFile.close ()
        configNewFile.close ()
        os.remove (configFile.name)
        os.rename (configNewFile.name, configFile.name)

    # 把客户端提交的流程原原本本还原执行
    for task in tasks :
        print (task [ "content" ])
        fname.write (task [ "content" ])

    # 组装文件结束
    fname.close ()

    # 寻找hrun路径
    args = "which hrun"
    print ("当前工作目录=" + os.getcwd ())
    pi = subprocess.Popen (args, shell=True, stdout=subprocess.PIPE)

    for i in iter (pi.stdout.readline, 'b') :
        if i != "" :
            hrunPath = str (i, encoding='utf-8')  # read出来是bytes，转成str
            print ("hrunPath=" + hrunPath)
            break
        else :
            print ("没有找到hrun哦...退出...")
            exit ()

    # 定位到hrun的相对路径执行（其实不是必须要，当时要解决路径中有空格的梗）
    hrunRelpath = os.path.relpath (hrunPath).rstrip ('\n')
    # 实际执行命令，hrun x.x.yml
    args = hrunRelpath + args_debug + args_report + " " + fname.name
    print ("执行命令 " + args)
    pi = subprocess.Popen (args, shell=True, stdout=subprocess.PIPE, cwd=os.getcwd ())

    returnString = ""
    result = "pass"
    user_id = ""
    SID = ""
    # 打印输出
    for i in iter (pi.stdout.readline, 'b') :
        if i != b'' :
            logLine = str (i, encoding='utf-8')
            logfile.writelines (logLine)  # 记录日志文件
            print ("==" + logLine)
            if logLine.find ("Generated Html report:") != -1 :
                # 提取报告路径，位于ice目录下，便于访问
                returnString = logLine.split (": ") [ 1 ].split ("html") [ 0 ] + "html"
                # 去掉ice目录，使得前端可以直接跳转
                reportPath = returnString.split ("/ice")
                # returnString 拼成一个json，包含report，结果，手机号
                returnString = "{\"result\":\"" + result + "\",\"reportPath\":\"" + reportPath [ 0 ] + reportPath [
                    1 ] + "\",\"logPath\":\"../reports/" + logfile.name.split ("/") [
                                   3 ] + "\",\"mobile\":\"" + newMobile + "\",\"user_id\":\"" + user_id + "\",\"SID\":\"" + SID + "\"}"

                os.remove (fname.name)  # todo:退出前删除执行文件，不够优雅
                logfile.close ()
                return returnString
            elif logLine.find ("ERROR") != -1 :
                # 失败检测
                result = "fail"
                print ("检测到校验失败了：" + logLine)
            elif logLine.find ("extract: content.user_id") != -1 :
                # 提取user_id, I konw this is silly code :)
                user_id = logLine.split ("=> ") [ 1 ].split ("[") [ 0 ].rstrip (stripP)
            elif logLine.find ("extract: cookies.SID") != -1 :
                # 提取SID用于返回
                SID = logLine.split ("=> ") [ 1 ].split ("[") [ 0 ].rstrip (stripP)
        else :
            # 无更多输出则结束
            os.remove (fname.name)  # todo:退出前删除执行文件，不够优雅
            logfile.close ()
            returnString = "{\"result\":\"" + result + "\",\"reportPath\":\"\",\"logPath\":\"../reports/" + \
                           logfile.name.split ("/") [
                               3 ] + "\",\"mobile\":\"" + newMobile + "\",\"user_id\":\"" + user_id + "\",\"SID\":\"" + SID + "\"}"
            return returnString


def gitPull() :
    args = "git pull"
    returnString = ""

    # automation目录
    print ("执行命令 " + args + " in " + os.getcwd ())
    pi = subprocess.Popen (args, shell=True, stdout=subprocess.PIPE, cwd=os.getcwd ())
    for i in iter (pi.stdout.readline, 'b') :
        if i != b'' :
            logLine = str (i, encoding='utf-8')
            print ("" + logLine)
            returnString += logLine
        else :
            # 无更多输出则结束
            break

    # ice目录
    icePath = os.path.abspath (os.path.join (os.getcwd (), "..")) + "/ice"
    print ("执行命令 " + args + " in " + icePath)
    pi = subprocess.Popen (args, shell=True, stdout=subprocess.PIPE, cwd=icePath)
    for i in iter (pi.stdout.readline, 'b') :
        if i != b'' :
            logLine = str (i, encoding='utf-8')
            print ("" + logLine)
            returnString += logLine
        else :
            # 无更多输出则结束
            break

    return returnString


def gitPush() :
    returnString = ""

    # 先pull
    args = "git pull"
    print ("执行命令 " + args + " in " + os.getcwd ())
    pi = subprocess.Popen (args, shell=True, stdout=subprocess.PIPE, cwd=os.getcwd ())
    for i in iter (pi.stdout.readline, 'b') :
        if i != b'' :
            logLine = str (i, encoding='utf-8')
            print ("" + logLine)
            returnString += logLine
        else :
            # 无更多输出则结束
            break

    # 然后add
    args = "git add ./"
    print ("执行命令 " + args + " in " + os.getcwd ())
    pi = subprocess.Popen (args, shell=True, stdout=subprocess.PIPE, cwd=os.getcwd ())
    for i in iter (pi.stdout.readline, 'b') :
        if i != b'' :
            logLine = str (i, encoding='utf-8')
            print ("" + logLine)
            returnString += logLine
        else :
            # 无更多输出则结束
            break

    # 再commit
    # todo: 前端给一个文本框输入提交注释
    args = "git commit -am 'commit from web'"
    print ("执行命令 " + args + " in " + os.getcwd ())
    pi = subprocess.Popen (args, shell=True, stdout=subprocess.PIPE, cwd=os.getcwd ())
    for i in iter (pi.stdout.readline, 'b') :
        if i != b'' :
            logLine = str (i, encoding='utf-8')
            print ("" + logLine)
            returnString += logLine
        else :
            # 无更多输出则结束
            break

    # 最后push
    args = "git push"
    print ("执行命令 " + args + " in " + os.getcwd ())
    pi = subprocess.Popen (args, shell=True, stdout=subprocess.PIPE, cwd=os.getcwd ())
    for i in iter (pi.stdout.readline, 'b') :
        if i != b'' :
            logLine = str (i, encoding='utf-8')
            print ("" + logLine)
            returnString += logLine
        else :
            # 无更多输出则结束
            break

    return returnString
