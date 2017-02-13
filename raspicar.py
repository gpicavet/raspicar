#!/usr/bin/env python3

from flask import Flask, request, render_template
from flask_socketio import SocketIO

import serial

app = Flask(__name__)
app.config['SECRET_KEY'] = 'raspicar'
socketio = SocketIO(app)

#create a serial interface with arduino at 9600 bit/s
ser = serial.Serial('/dev/ttyUSB0', 9600)

#write bytes to serial ouput
def sendCommand(c) :
    ser.write(c.encode("ascii"))

def sendData(d) :
    ser.write(bytearray(d))

#index route
@app.route('/')
def index():
    return render_template('index.html', mjpeg_serv_url='http://192.168.0.3:8080/?action=snapshot')

@socketio.on('is_connected')
def handle_message(message):
    print('received connexion: ' + str(message))

@socketio.on('command')
def handle_message(message):
    print('received command: ' + str(message))
    sendCommand(message["command"])
    p1 = 0;
    if "p1" in message["opts"] :
        p1 = message["opts"]["p1"];
    sendData([p1])

#start a server listening to all ip
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0")
