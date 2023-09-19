from datetime import datetime
import json
from flask import Flask, render_template, request
from flask_socketio import SocketIO, send, emit
from colors import *
import os
from random import randint

os.system("")
app = Flask(__name__)
socketio = SocketIO(app, ping_timeout=5000, ping_interval=10000)

connectedusers = {}


def genuid(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)


@app.route('/')
def homepage():
    return render_template('index.html')


@socketio.on('directmess')
def directmess(payload):
    message = payload["data"].strip()
    author = payload["author"].strip()
    to = payload["to"].strip()
    '''print(
        CVIOLET + author +
        CBEIGE + " to " +
        CVIOLET + connectedusers[int(to)]["username"] +
        CEND + ' : ' +
        CBLUE + message + CEND
    )'''
    responsejson = {
        "author": author,
        "content": message,
        "timestamp": datetime.now().timestamp()
    }
    emit("onmessage", responsejson, to=connectedusers[int(to)]["clientid"])


@socketio.on('connect')
def connect():
    userid = genuid(10)
    while userid in connectedusers:
        userid = genuid(10)
    emit('onconnect', {"uid": userid})


@socketio.on("joined")
def joined(payload):
    username = payload["user"]
    userid = payload["uid"]
    pubkey = payload["pubkey"]
    print(CGREEN2 + "Client connected as username: " +
          CYELLOW + username + CGREEN2 + " and id: " + CYELLOW + str(userid) + CEND)
    connectedusers[userid] = {
        "username": username,
        "clientid": request.sid,  # type: ignore
        "pubkey": pubkey
    }
    emit("userupdate", {"users": connectedusers}, broadcast=True)


@socketio.on("left")
def left(payload):
    uid = payload["uid"]
    print(CRED + "Client left as username: " +
          CYELLOW + connectedusers[uid]["username"] + CRED + " and id: " + CYELLOW + str(uid) + CEND)
    emit("userupdate", {"users": connectedusers}, broadcast=True)
    emit("userleft", {"uid": uid}, broadcast=True)
    connectedusers.pop(uid)


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
    print(CYELLOW + "Running on " + CBLUE + "http://127.0.0.1:5000" + CEND)
    socketio.run(app, host='0.0.0.0', port=5000)
