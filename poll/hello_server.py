#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''

'''
import zmq
import time
import threading

def process_in(sock):
    msg = sock.recv_string()
    if msg:
        print("{}".format(msg))
        time.sleep(1)
        sock.send_string('world')
        time.sleep(1)


def init_zmq():
    ctx = zmq.Context.instance()
    sock = ctx.socket(zmq.REP)
    sock.setsockopt(zmq.LINGER, 0)
    sock.bind('tcp://127.0.0.1:5555')
    return sock

def poll(sock):
    poller = zmq.Poller()
    poller.register(sock, zmq.POLLIN|zmq.POLLOUT)
    while True:
        for sock, event in poller.poll(2):
            if event & zmq.POLLIN:
                process_in(sock)
            
if __name__ == "__main__":
    sock = init_zmq()
    poll(sock)
