#!/usr/bin/env python3
import atexit
import logging

from flask import Flask, render_template, request
from flask_socketio import SocketIO

import serial
import signal,os,subprocess
import time
import threading

logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'raspicar'
socketio = SocketIO(app)


mjpeg_serv_port = 8080

# create a serial interface with arduino at 9600 bits/s
ser = serial.Serial('/dev/ttyUSB0', 9600)

appExit=False

# used to read data from arduino in background thread 
def readFromSerial():
    while not appExit:
       distance=""
       try:
          distance=float(ser.readline().decode())
       except:
          distance="error"
       logger.info("distance="+str(distance))
       time.sleep(0.5)

# write bytes to serial ouput
def sendCommand(com, data):
    ser.write(com.encode("ascii"))
    ser.write(bytearray(data))

def startMjpeg():
    global proc_mjpeg
    proc_mjpeg = subprocess.Popen('export LD_LIBRARY_PATH=/usr/local/lib/ && exec /usr/local/bin/mjpg_streamer -b -i "input_uvc.so" -o "output_http.so -p '+str(mjpeg_serv_port)+' -w ."', shell=True ,cwd='/usr/local/www')
    print("mjpeg started")

@atexit.register
def killMjpeg():
    proc_mjpeg.wait()
    for line in os.popen('ps ax | grep mjpg_streamer | grep -v grep'):
       os.kill(int(line.split()[0]), signal.SIGKILL)
    print("mjpeg stopped")

# index route
@app.route('/')
def index():
    host = request.headers['Host']
    sep = host.find(":")
    if(sep > 0) :
        host = host[0:sep]
    return render_template('index.html', mjpeg_serv_url='http://' + host + ':' + str(mjpeg_serv_port) + '/?action=snapshot')

@app.route('/sonar')
def handle_sonar():
    if(ser.isWaiting()) :
       logging.info("distance = "+ser.readline())
    return "ok"

@socketio.on('is_connected')
def handle_connect(message):
    logging.info('received connexion: ' + str(message))

@socketio.on('command')
def handle_command(message):
    logging.info('received command: ' + str(message))
    opts = message["opts"]
    if len(opts) == 0:  # FIXME send data length
        opts = [0]
    sendCommand(message["command"], opts)

@socketio.on('read')
def handle_read(message):
    if(ser.isWaiting()) :
        logging.info("distance = "+ser.readline())

# start a server listening to all ip
if __name__ == "__main__":
  try:
    startMjpeg()
    thread = threading.Thread(target=readFromSerial)
    thread.start()
    socketio.run(app, host="0.0.0.0")
  except KeyboardInterrupt:
    appExit=True
    raise
