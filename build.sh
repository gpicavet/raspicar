#!/bin/bash

npm install
mkdir -p static/lib
cp node_modules/jquery-ui-dist/jquery-ui.min.css static/lib
cp node_modules/jquery/dist/jquery.min.js static/lib
cp node_modules/jquery-ui-dist/jquery-ui.min.js static/lib
cp node_modules/jquery-ui-touch-punch/jquery.ui.touch-punch.min.js static/lib
cp node_modules/socket.io-client/dist/socket.io.min.js static/lib

mkdir -p build
tar zcf build/raspicar.tar.gz static templates raspicar.py
