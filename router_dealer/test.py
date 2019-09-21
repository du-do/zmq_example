#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
ROUTER-DEALER 路由
ROUTER 将消息发送给指定的DEALER，DEALER不需要处理信封
'''


import zmq
import time
import threading


def task_a():
    ctx = zmq.Context.instance()
    worker  = ctx.socket(zmq.DEALER)
    # 为套接字添加认证信息
    worker.setsockopt_string(zmq.IDENTITY, 'A')
    worker.connect("ipc://routing.ipc")

    total = 0
    while True:
        msg = worker.recv_multipart()
        print('task a msg:{}'.format(msg))

        if msg[1] == b'END':
            print('task a total:%d' % total)
            break
        total += 1
    
    worker.close()
    ctx.term()

def task_b():
    ctx = zmq.Context.instance()
    worker  = ctx.socket(zmq.DEALER)
    # 为套接字添加认证信息
    worker.setsockopt_string(zmq.IDENTITY, 'B')
    worker.connect("ipc://routing.ipc")

    total = 0
    while True:
        msg = worker.recv_multipart()
        print('task b msg:{}'.format(msg))

        if msg[1] == b'END':
            print('task b total:%d' % total)
            break
        total += 1
    
    worker.close()
    ctx.term()

if __name__ == "__main__":
    ctx = zmq.Context.instance()
    router  = ctx.socket(zmq.ROUTER)
    router.bind("ipc://routing.ipc")

    task_a = threading.Thread(target=task_a)
    task_b = threading.Thread(target=task_b)

    task_a.start()
    task_b.start()
    # 延迟 1 秒，等待DEALER与ROUTER建立连接，未建立连接时ROUTER发送的消息会丢失
    time.sleep(1)

    msg = []
    msg.append(b'A') # ROUTER 发送时会将此消息拿掉。DEALER不会收到此消息
    msg.append(b'') # 也可以没有这个消息
    msg.append(b'hello world')

    for task_nbr in range(5):
        msg[0] = b'A'
        # 向 task a 发送两次
        router.send_multipart(msg)
        router.send_multipart(msg)

        msg[0] = b'B'
        router.send_multipart(msg)

    # 准备结束消息
    msg[2] = b'END'

    msg[0] = b'A'
    router.send_multipart(msg)
    msg[0] = b'B'
    router.send_multipart(msg)

    task_a.join()
    task_b.join()

    router.close()
    ctx.term()



























