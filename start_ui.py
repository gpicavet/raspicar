#!/usr/bin/env python

from flask import Flask, request, render_template
import serial

app = Flask(__name__)

#create a serial interface at 9600 bit/s
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

#command route
@app.route('/c/<string:com>')
def command(com):
    sendCommand(com)

    p1 = request.args.get("p1",0, type=int)
    sendData([p1])

    return ""

#start a server listening to all ip
if __name__ == "__main__":
    app.run(host='0.0.0.0')
