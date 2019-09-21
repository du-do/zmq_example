#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
+--------+  +--------+  +--------+
| Client |  | Client |  | Client |
+--------+  +--------+  +--------+
|  REQ   |  |  REQ   |  |  REQ   |
+---+----+  +---+----+  +---+----+
    |           |           |
    +-----------+-----------+
                |
            +---+----+
            | ROUTER |
            +--------+
            | Device |
            +--------+
            | DEALER |
            +---+----+
                |
    +-----------+-----------+
    |           |           |
+---+----+  +---+----+  +---+----+
|  REP   |  |  REP   |  |  REP   |
+--------+  +--------+  +--------+
| Worker |  | Worker |  | Worker |
+--------+  +--------+  +--------+

REQ套接字在发送消息时会向头部添加一个空帧，接收时又会自动移除。ROUTER会在所有收到的消息前添加消息来源的地址。
Figure # - Stretched request-reply
'''
import zmq
import time
import threading

# 前段客户端
def client_task():
    ctx = zmq.Context.instance()
    worker  = ctx.socket(zmq.REQ)
    # 为套接字添加认证信息，认证信息为线程名字
    worker.setsockopt_string(zmq.IDENTITY, threading.current_thread().name)
    worker.connect("ipc://frontend.ipc")
    
    time.sleep(1)
    # 向frontend router 发送请求
    worker.send_string('hello')
    # 等待回应
    msg = worker.recv_string()
    # do something
    print('{} : msg {}'.format(threading.current_thread().name, msg) )
    while True:
        time.sleep(5)
    worker.close()
    ctx.term()

# 后端处理器
def worker_task():
    ctx = zmq.Context.instance()
    worker  = ctx.socket(zmq.REQ)
    # 为套接字添加认证信息，认证信息为线程名字
    worker.setsockopt_string(zmq.IDENTITY, threading.current_thread().name)
    worker.connect("ipc://backend.ipc")
    # 向ROUTER发送ready，然后阻塞，等待backend ROUTER 分配任务
    worker.send_string('ready')
    while True:
        # 接收 backend ROUTER 分配的任务
        msg = worker.recv_multipart()
        print('{} get request: {}'.format(threading.current_thread().name, msg))

        # 设置回应
        msg[2] = b'world'
        # 向 backend ROUTER 发送回应
        worker.send_multipart(msg)


    worker.close()
    ctx.term()

if __name__ == "__main__":
    ctx = zmq.Context.instance()
    frontend  = ctx.socket(zmq.ROUTER)
    backend  = ctx.socket(zmq.ROUTER)
    frontend.bind("ipc://frontend.ipc")
    backend.bind("ipc://backend.ipc")

    # 注册 poller
    poller = zmq.Poller()
    poller.register(frontend, zmq.POLLIN)
    poller.register(backend, zmq.POLLIN)
    
    # 启动客户端线程
    for b_nbr in range(3):
        worker = threading.Thread(target=worker_task, name='worker'+str(b_nbr))
        worker.start()
    # 启动服务端线程
    for c_nbr in range(3):
        client = threading.Thread(target=client_task, name='client'+str(c_nbr))
        client.start()
    # 空闲的worker
    worker_queue = []

    while True:
        for sock, event in poller.poll(2):
            if sock == backend:
                msg = sock.recv_multipart()
                # 收到消息说明这个worker已经空闲，保存空闲worker address
                worker_queue.append(msg[0])
                print('worker address %s' % msg[0])
                # 如果消息体是 ready 说明是刚启动。如果不是ready说明消息里带了回应
                if msg[2] != b'ready':
                    # frontend 的 ROUTER 向client 回复
                    frontend.send_multipart(msg[2:])
            else:
                msg = sock.recv_multipart()
                # frontend 的 ROUTER 收到了client的请求，找一个空闲worker，将请求通过backend ROUTER 转给它
                new_msg = [worker_queue.pop(), b'']
                # 与client的请求组成新消息
                new_msg = new_msg + msg
                print('new msg {}'.format(new_msg))
                # 将请求转给空闲 worker
                backend.send_multipart(new_msg)




















    











