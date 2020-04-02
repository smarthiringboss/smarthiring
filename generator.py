import requests
import json
import os

print(os.getcwd())
pre_path = os.path.abspath(os.getcwd())+"/test_java_code/"

def get_swagger(appId):
    kw = {'wd': '长城'}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36"}

    # params 接收一个字典或者字符串的查询参数，字典类型自动转换为url编码，不需要urlencode()
    response = requests.get("http://stargate.elenet.me/base.apiportal_ops/api/"+appId+"/BETA/swaggerJson?type=1", params=kw, headers=headers)

    fname = open('downloadedSwagger.json', "w")
    content = json.loads(response.text)
    data = content["data"]
    if data=="{}":
        return "fail"
    fname.write(data)
    fname.close()
    return "pass"

# 取最后一个.值
def getLast(longdotString):
    s = longdotString.split(".")
    return s[len(s)-1]

# 首字符转大写
def upperFirstS(s):
    return s[0].upper()+s[1:len(s)]

# 根据property类型做转换
def format_property(property, properties):
    print("property=" + property)
    if property == "taobaoId" :
        print (property)
    # 所有属性的转型都由type或者format决定
    if "type" in properties [ property ] :
        type = properties [ property ] [ "type" ]
    else :
        type = ""
    if "format" in properties [ property ] :
        format = properties [ property ] [ "format" ]
    else :
        format = ""
    print ("type=" + type)
    print ("format=" + format)

    if ("Id" in property or "id" in property or "Time" in property or "time" in property) and type != "string" :
        formated_property = "Long.valueOf(" + property + ")"
    elif format == "byte" :
        formated_property = "Byte.valueOf(" + property + ")"
    elif format == "int64" or format == "int32" :
        formated_property = "Integer.valueOf(" + property + ")"
    elif format == "double" :
        formated_property = "Double.valueOf(" + property + ")"
    elif format == "date" :
        formated_property = "(long) LocalDateTime.now().getSecond()"
    elif format == "date-time" :
        formated_property = "Date.valueOf(" + property + ")"
    elif format == "boolean" :
        formated_property = "Bolean.valueOf(" + property + ")"
    elif format == "" and type == "string" :
        formated_property = "String.valueOf(" + property + ")"
    elif format == "" and type == "boolean" :
        formated_property = "Boolean.valueOf(" + property + ")"
    elif format == "" and type == "array" :
        formated_property = "Array.valueOf(" + property + ")"
    elif format == "" and type == "object" :
        formated_property = "(Object) " + property + ""
    else :
        print ("err, can't recognize the type")
        formated_property = "" + property + ""

    return formated_property

# 产生文件内容
def generate_file_content(operation, swagger):
    # 每个引用对象
    definitions = swagger["definitions"]

    class_name = operation["x-java-class-name"]
    parameters = operation['x-stargate-parameters']
    return_class = operation['x-stargate-returns']

    file_content = "package com.alibaba.alsc.elemember."+getLast(class_name)+";\n\n"
    file_content += "import java.util.Map;\n"
    file_content += "import com.alibaba.alsc.ele.EleRpcContext;\n"
    file_content += "import com.alibaba.alsc.ele.EleRpcInvokeUtil;\n"
    file_content += "import com.alsc.hotload.exec.ExecComp;\n"
    file_content += "import com.alsc.hotload.exec.ExecResult;\n"
    file_content += "import com.alsc.hotload.util.LogUtil;\n"
    file_content += "import com.alsc.testengine.util.AssertUtil;\n"
    file_content += "import com.taobao.hsf.util.ExceptionUtil;\n"

    # 引用-----
    # 服务名
    file_content += "import "+class_name+";\n"
    # 参数列表 - 多个
    for parameter in parameters:
        # 原生对象不import
        if "java." not in parameters[parameter]:
            file_content += "import " + parameters[parameter] + ";\n\n"
    # 返回值 - 原生对象不import
    if "." in return_class:
        file_content += "import "+return_class+";\n\n"

    file_content += operation['x-handler-handlerMethod']+"\n"
    file_content += "public class "+"Test"+upperFirstS(operation["x-java-method-name"])+" implements ExecComp {\n\n"
    # 服务实例
    file_content += "  private "+class_name+" service;\n\n"
    file_content += "  @Override\n"
    file_content += "  public void init() {\n"
    file_content += "    service = EleRpcInvokeUtil.bindingRpc("+getLast(class_name)+".class,\""+operation['x-application-id']+"\");\n"
    file_content += "  }\n\n"
    file_content += "  /* 详细打包信息，有助于debug\n"
    file_content += "    " + json.dumps(operation['x-info']['descriptions'], indent=4, ensure_ascii=False)
    file_content += "  */ \n"
    file_content += "  @Override\n"
    file_content += "  public ExecResult run(Map<String, String> map) {\n"
    file_content += "    ExecResult result = new ExecResult();\n\n"

    # 赋值-----
    # 参数列表 - 多个
    for parameter in parameters:

        # 内置类型
        if "java." in parameters[parameter]:
            file_content += "    // java internnal object, 暂时手工修改\n"
            file_content += "    " + parameters[parameter] + " " + parameter + " = null;\n"
        # 引用类型
        else:
            file_content += "    " + getLast(parameters[parameter]) + " " + parameter + " = new " + getLast(parameters[
                parameter]) + "();\n"

            # 有些引用类型在definitions里面找不到
            para_type = getLast(parameters[parameter])
            if para_type in definitions:
                properties = definitions[para_type]["properties"]
                # 每个属性的定义
                for property in properties:
                    if "description" in properties [ property ] :
                        description = properties [ property ] [ "description" ]
                    else :
                        description = "此参数无注解"
                    file_content += "    // " + description + "\n"
                    file_content += "    String " + property + " = null;\n"

                # 每个属性的默认值
                file_content += "\n"
                for property in properties :
                    file_content += "    //" + property + " = map.get(\"" + property + "\");\n"

                # 每个属性的默认值
                file_content += "\n"
                for property in properties :
                    file_content += "    if (" + property + "==null) { " + property + "=\"111\";}\n"

                # 每个属性的转型
                file_content += "\n"
                for property in properties :
                    file_content += "    if ("+property+"!=null) {"
                    file_content += " "+parameter+".set"+upperFirstS(property)+"("+format_property(property, properties)+");"
                    file_content += " }\n"

    # 返回值
    if "." in return_class:
        file_content += "\n    " + getLast(return_class) + " response = new "+getLast(return_class)+"();\n"
    elif "void" in return_class:
        file_content += "\n    Object response;\n"
    else:
        file_content += "\n    " + getLast(return_class) + " response;\n"
    file_content += "    try {\n"
    file_content += "      response = service."+operation['x-java-method-name']+"("
    # 逗号计数，恶心
    count_1 = 0
    for parameter in parameters:
        if  count_1 != 0:
            file_content += ","+parameter
        else:
            file_content += parameter
        count_1 += 1
    file_content += ");\n"
    file_content += "    } catch (Exception e) {\n"
    file_content += "      LogUtil.log(\"exception e {0}\", ExceptionUtil.getStackTrace(e));\n"
    file_content += "    }\n\n"

    # 判断-----
    file_content += "    //AssertUtil.equal(\"success\", response.getResponseHeader().getMessage(), \"购买成功\");\n"
    file_content += "    //result.putResult(\"message\",response.getResponseHeader().getMessage());\n"
    file_content += "    return result;\n"
    file_content += "    }\n"
    file_content += "  }\n"

    return file_content

# 生成文件
def generate_file(file_name, file_content):
    file_name = pre_path+file_name
    isExists = os.path.exists(os.path.dirname(file_name))
    if not isExists:
        # 如果不存在则创建目录
        os.makedirs(os.path.dirname(file_name))
    file = open(file_name, "w+")
    file.write(file_content)
    file.close()

def generate_code(appId):
    if get_swagger(appId)=="fail":
        return "{\"result\":\"fail\"}"

    swagger_json_file = open("downloadedSwagger.json", "r")
    swagger = json.loads(swagger_json_file.read())

    print(swagger)

    # 每个接口
    paths = swagger["paths"]
    print(paths)
    for path_key in paths:
        path = paths[path_key]
        if "post" in path:
            operation = path["post"]
            # print(operation["x-java-method-name"])
            #if "makeSupervipOrde" in operation["x-java-method-name"]:
                # 生成内容
            content = generate_file_content(operation, swagger)
                # 写入文件
            generate_file(getLast(operation['x-stargate-class'])+"/Test"+upperFirstS(operation["x-java-method-name"])+".java", content)

    return "{\"result\":\"pass\"}"


# 根据debug是obj的值生成一批默认值代码
def convert_code(ori_obj):
    return_string = ""
    obj_list = ori_obj.split (",")
    for obj in obj_list :
        obj_key = obj.split ("=") [ 0 ]
        obj_value = obj.split ("=") [ 1 ]
        if obj_value != "null" :
            print ("if (" + obj_key + "==null) { " + obj_key + "=\"" + obj_value + "\";}\n")
            return_string += "if (" + obj_key + "==null) { " + obj_key + "=\"" + obj_value + "\";}\n"
        else :
            print ("if (" + obj_key + "==null) { " + obj_key + "=null;}\n")
            return_string += "if (" + obj_key + "==null) { " + obj_key + "=null;}\n"
    # return "{\"result\":\"pass\",\"code\":\""+return_string+"\"}"
    return return_string
