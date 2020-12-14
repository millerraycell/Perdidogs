from flask.json import jsonify
import pymongo
import json
from bson import json_util
from flask import Flask, request
from flask_cors import CORS
from pymongo.mongo_client import MongoClient
from config.settings import MONGO_CONNECTION

def parse_json(data):
    return json.loads(json_util.dumps(data))

app = Flask(__name__)

CORS(app)

conn = MongoClient(MONGO_CONNECTION)

db = conn.perdidogs

collection = db.animais

@app.route("/", methods=["GET", "POST"])
def execucao():
    if request.method == "GET":
        dados = []

        for post in collection.find():
            dados.append(post)

        print(dados)

        return json.dumps(dados, default=str)

if __name__ == '__main__':
    app.run(host='0.0.0.0')



