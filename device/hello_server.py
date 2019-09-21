#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import zmq
import time

ctx = zmq.Context.instance()
socket = ctx.socket(zmq.PULL)
socket.setsockopt(zmq.LINGER, 0)
socket.connect('tcp://127.0.0.1:5556')

while True:
    message = socket.recv_string()
    print('{}'.format(message))
    