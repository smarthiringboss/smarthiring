#!flask/bin/python
from flask import Flask, jsonify
from flask import make_response
from flask import request
from flask_cors import cross_origin, CORS

import tasks
import generator
import fetch

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://smarthiring:Startnewlife2008@localhost/smart_hiring'
cors = CORS(app, resources={r"/tasks/*": {"origins": "*"}})

iTasks = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol',
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web',
        'done': False
    }
]

@app.route('/gitpull', methods=['GET'])
@cross_origin()
def git_pull():
    return tasks.gitPull()

@app.route('/gitpush', methods=['GET'])
@cross_origin()
def git_push():
    return tasks.gitPush()

@app.route('/tasks/v1/refreshgeeks/<string:mail>', methods=['POST'])
@cross_origin()
def goto_task(mail):
    if not request.json or not mail:
        # 此处提交json用于未来扩展
        # 可从前端设置一些变量传到后端用于config.yml
        not_found(400)
    # 默认打开debug选项
    returnString = fetch.fetch_geeks(request.json, mail)
    print("准备从goto_task返回")

    return returnString, 201

@app.route('/tasks/v1/save/<string:laneId>/<string:fileName>', methods=['POST'])
@cross_origin()
def save_task(laneId, fileName):
    if not request.json or not 'lanes' in request.json:
        # 此处提交json用于未来扩展
        # 可从前端设置一些变量传到后端用于config.yml
        not_found(400)
    # 默认打开debug选项
    returnString = tasks.save_tasks(request.json, laneId, fileName)

    return returnString, 201

@app.route('/tasks/fetchtestcases', methods=['POST'])
@cross_origin()
def fetchTestcases():
    returnString = tasks.fetch_testcases()
    return returnString, 201

@app.route('/tasks/v1/query/<string:fileName>', methods=['POST'])
@cross_origin()
def queryTestcase(fileName):
    returnString = tasks.query_testcases(fileName)
    return returnString, 201

@app.route('/tasks/fetchall', methods=['POST'])
@cross_origin()
def fetchTasks():
    returnString = tasks.fetch_tasks()
    return returnString, 201

@app.route('/code/view', methods=['POST'])
@cross_origin()
def get_code():
    if not request.json or not 'path' in request.json:
        # 此处提交json用于未来扩展
        not_found(400)

    returnString = tasks.get_code(request.json["path"])
    return returnString, 201

@app.route('/code/submit', methods=['POST'])
@cross_origin()
def submit_code():
    if not request.json or not 'path' in request.json:
        # 此处提交json用于未来扩展
        not_found(400)
    print(request.data)
    returnString = tasks.submit_code(request.json["path"], request.json["codePiece"])
    return returnString, 201

@app.route('/code/generate', methods=['POST'])
@cross_origin()
def generate_code():
    print("Martin is in....")
    if not request.json or not 'appId' in request.json:
        # 此处提交json用于未来扩展
        not_found(400)
    returnString = generator.generate_code(request.json["appId"])
    return returnString, 201

@app.route('/code/convert', methods=['POST'])
@cross_origin()
def convert_code():
    if not request.json or not 'obj' in request.json:
        # 此处提交json用于未来扩展
        not_found(400)
    returnString = generator.convert_code(request.json["obj"])
    return returnString, 201

@app.route('/code/pullall', methods=['POST'])
@cross_origin()
def get_all_files():
    return tasks.get_all_files()

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

if __name__ == '__main__':
    print("service is up!...")
    app.run(
        host='0.0.0.0',
        port= 9999,
        debug=False
    )