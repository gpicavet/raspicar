#!/usr/bin/env python3

import logging

from flask import Flask, render_template, request
from flask_socketio import SocketIO

import os
import serial

app = Flask(__name__)
app.config['SECRET_KEY'] = 'raspicar'
socketio = SocketIO(app)

mjpeg_serv_port = 8080

# create a serial interface with arduino at 9600 bits/s
ser = serial.Serial('/dev/ttyUSB0', 9600)

# write bytes to serial ouput
def sendCommand(com, data):
    ser.write(com.encode("ascii"))
    ser.write(bytearray(data))

# index route
@app.route('/')
def index():
    ip = request.remote_addr
    return render_template('index.html', mjpeg_serv_url='http://' + ip + ':' + mjpeg_serv_port + '/?action=snapshot')

@app.route('/mjpeg')
def mjpeg():
    os.system('/usr/local/bin/mjpg_streamer -i "/usr/local/lib/input_uvc.so" -o "/usr/local/lib/output_http.so -w /usr/local/www"')
    return ""

@socketio.on('is_connected')
def handle_message(message):
    logging.info('received connexion: ' + str(message))


@socketio.on('command')
def handle_message(message):
    logging.info('received command: ' + str(message))
    opts = message["opts"]
    if len(opts) == 0:  # FIXME send data length
        opts = [0]
    sendCommand(message["command"], opts)

# start a server listening to all ip
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0")
