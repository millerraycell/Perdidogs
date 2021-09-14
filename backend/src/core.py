import json

from bson import json_util, objectid
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

@app.route("/", methods=["GET"])
def index():
    if request.method == "GET":
        dados = []

        latitude = request.args.get("latitude", type=float)
        longitude = request.args.get("longitude", type=float)
        max_dist = request.args.get("max_dist", default=100000,type=int)

        data = collection.aggregate([{"$geoNear":{
            "near" : {
                "type":"Point",
                "coordinates":[latitude, longitude]
            },
            "distanceField":"dist.calculated",
            "maxDistance": max_dist,
            "spherical": True
        }}])

        for post in data:
            info = {
                "_id" : post["_id"],
                "images" : post["images"],
                "latitude" : post["geometry"]["coordinates"][0],
                "longitude" : post["geometry"]["coordinates"][1],
                "date" : post["date"]
            }
            dados.append(info)

        return json.dumps(dados, default=str)

@app.route("/post", methods=["GET"])
def show():
    if request.method == "GET":
        id = request.args.get("id", type=str)

        animal = collection.find_one({"_id": objectid.ObjectId(id)})

        return json.dumps(animal, default=str)

if __name__ == '__main__':
    app.run(host='0.0.0.0')



