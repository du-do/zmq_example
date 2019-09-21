#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import zmq
import time
from threading import Thread

def client(ctx):
    socket = ctx.socket(zmq.PUSH)
    socket.connect('inproc://127.0.0.1:5555')

    while True:
        socket.send_string('hello ')
        time.sleep(1)

def server(ctx):
    socket = ctx.socket(zmq.PULL)
    socket.bind('inproc://127.0.0.1:5555')

    while True:
        message = socket.recv_string()
        print('{}'.format(message))
        time.sleep(1)

if __name__ == "__main__":
    ctx = zmq.Context.instance()
    consumer = Thread(target=server, args=(ctx,))
    producer = Thread(target=client, args=(ctx,))

    consumer.start()
    producer.start()

    consumer.join()
    producer.join()