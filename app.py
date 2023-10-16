
from server import Server
from flask import jsonify, request
from flask_cors import cross_origin
from celery.result import AsyncResult
import uuid
import os
import shutil
from services.processDocs import process
from services.model import Model

server = Server(__name__)

rds = server.redis
celery = server.celery
app = server.app
socket = server.socketio
db = server.db


@app.route('/createbot', methods=['POST'])
@cross_origin()
def upload_files():
    print(request)
    rds_task_id = str(uuid.uuid4())
    if 'files' not in request.files:
        return jsonify({"message": "No file uploaded"})
    files = request.files.getlist('files')

    # for testing
    for file in files:
        print(file.filename)

    # LLM operation
    data = process(uploaded_file=files)
    print("*******:", data)
    kwargs = {"data": data, "callback_api": "http://127.0.0.1:5000/callback_result",
              "rds_task_id": rds_task_id, "name": request.form["name"]}
    task = celery.send_task("tasks.create_bot", kwargs=kwargs)
    # ------

    # for handling callback api
    rds.set(rds_task_id, task.id)
    return jsonify({"taskId": task.id})

# Executes after celery task done -> Callback API


@app.route('/callback_result', methods=['POST'])
def callback_result():
    data = request.get_json()
    print("socketid::",data)
    # import time
    # time.sleep(4)
    
    socket.emit(str(data["task_id"]), data)
    return jsonify("done")


@app.route('/chat', methods=['POST'])
@cross_origin()
def get_response():
    rds_task_id = str(uuid.uuid4())
    # # it will come from uploaded docs
    req_data = request.get_json()
    llm = Model()
    # result = llm.get_response_from_watsonx(data=_data)
    result = llm.get_response_singelton(data=req_data)
  
    kwargs = {"data": result, "callback_api": "http://127.0.0.1:5000/callback_result",
              "rds_task_id": rds_task_id}
    task = celery.send_task("tasks.chat_bot", kwargs=kwargs)
    
    rds.set(rds_task_id, task.id)
    return jsonify({"taskId": task.id})

    # data = "appended data"
    # kwargs = {"_data": req_data, "callback_api": "http://127.0.0.1:5000/callback_result",
    #           "rds_task_id": rds_task_id}
    # task = celery.send_task(
    #     "tasks.get_response", kwargs=kwargs)
    # # ------

    # # for handling callback api
    # rds.set(rds_task_id, task.id)
    # return jsonify({"taskId": task.id})



# Instead of this API , I used socket-> for avoiding multiple request from client
@app.route("/task/<task_id>", methods=["GET"])
@cross_origin()
def get_result(task_id):

    result = AsyncResult(task_id, app=celery)
    response_data = {
        "taskId": task_id,
        "taskStatus": result.status,
        "taskResult": result.result

    }

    print(response_data)

    return jsonify(response_data)

# post route for create bots


@app.route('/delete_bot/<id>', methods=['DELETE'])
def delete_file(id):
    try:
    # name = request.get_json()["name"]
        obj = db.vectordb.find({"_id": id})
        name = obj[0]["name"]
        db.vectordb.delete_many({"name": name}) 
        file_path = os.path.join('./vector_db_store', name)
        print(file_path)
        if os.path.exists(file_path):
            shutil.rmtree(file_path)
            return jsonify({'message': f'File {name} deleted successfully'})
        else:
            return jsonify({'message': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/listbot', methods=['GET'])
def list_bot():
    # data = [
    #     {
    #         "id": "4b21a548-6a9b-11ee-8c99-0242ac120002",
    #         "name": "HDFC"

    #     },
    #     {
    #         "id": "69df5840-6a9b-11ee-8c99-0242ac120002",
    #         "name": "SBI"

    #     }
    # ]
    mongod = db.vectordb.find({},{"name":1,"id":1,"status":1,"_id":0})
    res=list(mongod)
    return jsonify(res)

# OTP verify


@app.route("/verifyadmin", methods=["POST"])
@cross_origin()
def verify_otp():
    data = request.get_json()
    if data["password"] == "admin":
        status = True
    else:
        status = False
    response_data = {
        "status": status

    }

    return jsonify(response_data)


if __name__ == '__main__':
    server.run()
