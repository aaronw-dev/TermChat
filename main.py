from datetime import datetime
import json
from flask import Flask, render_template, request
from flask_socketio import SocketIO, send, emit
from colors import *
import os
os.system("")
app = Flask(__name__)
socketio = SocketIO(app)

connectedusers = []


@app.route('/')
def homepage():
    return render_template('index.html')


@socketio.on('connect')
def connect():
    emit('onconnect')


@socketio.on("joined")
def joined(payload):
    username = payload["user"]
    print(CGREEN2 + "Client connected as username: " + CYELLOW + username + CEND)
    connectedusers.append(username)
    emit("userupdate", {"users": connectedusers}, broadcast=True)


@socketio.on("left")
def left(payload):
    username = payload["user"]
    connectedusers.remove(username)
    print(CRED + "Client left as username: " + CYELLOW + username + CEND)
    emit("userupdate", {"users": connectedusers}, broadcast=True)
    emit("userleft", {"user": username}, broadcast=True)


@socketio.on('message')
def handle_message(data):
    message = data["data"].strip()
    author = data["author"].strip()
    pubkey = data["publickey"].strip()
    print(CVIOLET + author + CEND + ' : ' + CBLUE + message + CEND)
    responsejson = {
        "author": author,
        "content": message,
        "timestamp": datetime.now().timestamp(),
        "pubkey": pubkey
    }
    emit("onmessage", responsejson, broadcast=True)


@socketio.on('ping')
def ping():
    emit("pingresponse")


@app.errorhandler(500)
def fivehundrederror(error):
    return render_template("error.html", errorcode=error)


@app.errorhandler(404)
def invalid_route(error):
    return render_template("error.html")


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    print(CYELLOW + "Running now." + CEND)
    socketio.run(app, host='0.0.0.0', port=5000)
