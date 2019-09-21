#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import zmq
import time

ctx = zmq.Context.instance()
socket = ctx.socket(zmq.PUSH)
socket.connect('tcp://127.0.0.1:5555')

while True:
    socket.send_string('hello ')
    time.sleep(1)