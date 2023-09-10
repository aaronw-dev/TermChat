from datetime import datetime
import json
from flask import Flask, render_template, request
from flask_socketio import SocketIO, send, emit
from colors import *
import os
os.system("")
app = Flask(__name__)
socketio = SocketIO(app)

opensockets = []


@app.route('/')
def homepage():
    return render_template('index.html')


@socketio.on('connect')
def test_connect():
    print(CGREEN2 + "Client connected." + CEND)
    emit('onconnect', {'data': 'Connected'})


@socketio.on('disconnect')
def test_disconnect():
    print(CRED + 'Client disconnected' + CEND)


@socketio.on('message')
def handle_message(data):
    message = data["data"]
    message = message.strip()
    print('received message: ' + CBLUE + message + CEND)
    responsejson = {
        "author": "server",
        "content": "This is what you said: \"" + message + "\" at " + datetime.now().strftime("%H:%M"),
        "timestamp": datetime.now().timestamp()
    }
    emit("serverresponse", responsejson, broadcast=True)


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
