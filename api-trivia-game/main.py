import os
from os.path import join, dirname
import requests
from flask import Flask, jsonify, abort
from flask_cors import CORS
from dotenv import load_dotenv
import pyrebase
import json

#
# configuracion para obtener los datos de variable de entorno.
#
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
# Configuracion de flask
app = Flask(__name__)
CORS(app)

# Configuracion de firebase
conf = {
    "apiKey": os.environ.get("apiKey"),
    "authDomain": os.environ.get("authDomain"),
    "databaseURL": os.environ.get("databaseURL"),
    "storageBucket": os.environ.get("storageBucket")
}

firebase = pyrebase.initialize_app(conf)
db = firebase.database()


@app.route('/')
def init():
    response = {
        "category_list": "/categories",
        "difficulty_list": "/difficulties",
    }
    return jsonify(response)


# *
# Difficulty
# *#
@app.route('/difficulties', methods=['GET'])
def getDifficulties():
    response = ""
    try:
        response = db.child("trivia").child("difficulties").get().val()
    except Exception as e:
        print(e)
        abort(500)
    return json.dumps(response)


@app.route('/set-difficulty/<difficulty_name>/<int:difficulty_value>')
def setDifficulty(difficulty_name, difficulty_value):
    try:
        id = 0
        if (db.child("trivia").child("difficulties").get().val() != None):
            if (len(db.child("trivia").child("difficulties").get().val()) > 0):
                id = len(db.child("trivia").child("difficulties").get().val())
        if (difficulty_name != None and difficulty_value != None):
            db.child("trivia").child("difficulties").push({
                "id": id,
                "name": difficulty_name,
                "value": difficulty_value
            })
    except Exception as e:
        print(e)
        abort(500)
    return "Ok"


# *
# Category
# *#
@app.route('/set-category', methods=['GET'])
def setCategory():
    response = ""
    try:
        categories = requests.get(os.environ.get("opendbCategoryEndpoint"))
        if (categories.ok and categories.status_code == 200):
            for category in categories.json()["trivia_categories"]:
                db.child("trivia").child("categories").push({
                    "id": category["id"],
                    "name": category["name"]
                })
            response = {
                "ok": categories.ok
            }
    except Exception as e:
        print(e)
        abort(500)
    return response


@app.route('/categories', methods=['GET'])
def getCategory():
    response = ""
    try:
        response = db.child("trivia").child("categories").get().val()
    except Exception as e:
        print(e)
        abort(500)
    return json.dumps(response)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
