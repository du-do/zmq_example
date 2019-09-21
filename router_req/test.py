#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
ROUTER-REQ 示例，最近最少使用算法路由
REQ套接字在处理完任务后会主动发送 ready 
REQ套接字在发送 ready 后，进入接收消息状态，如果没消息，进入阻塞状态。
ROUTER 在收到 ready 后，就表明 发送消息的 REQ 套接字是空闲的，且现在是阻塞等待任务的。
'''

import zmq
import time
import threading


def worker_task():
    time.sleep(5)
    ctx = zmq.Context.instance()
    worker  = ctx.socket(zmq.REQ)
    # 为套接字添加认证信息，认证信息为线程名字
    worker.setsockopt_string(zmq.IDENTITY, threading.current_thread().name)
    worker.connect("ipc://routing.ipc")
    total = 0
    while True:
        # 发送ready，表明可接受任务
        worker.send_string('ready')
        # 等待任务分配，ROUTER 不给其返回消息时，阻塞
        msg = worker.recv_string()
        # 如果为 END 则表明 ROUTER 已没有任务可分配给指定 REQ 了，REQ 准备退出
        if msg == 'END':
            print('process %d' % total)
            break
        # do something，计数
        total += 1
        time.sleep(0.2)

    worker.close()
    ctx.term()


if __name__ == "__main__":
    ctx = zmq.Context.instance()
    client  = ctx.socket(zmq.ROUTER)
    client.bind("ipc://routing.ipc")
    tasks = []
    # 创建线程
    for num in range(2):
        tasks.append(threading.Thread(target=worker_task, name='task'+str(num)))
    # 启动线程
    for task in tasks:
        task.start()

    for task_nbr in range(len(tasks)*10):
        # 接收多帧消息，消息内容为byte类型
        msg = client.recv_multipart()
        print('msg:{}'.format(msg))

        msg[2] = b'hello world'
        client.send_multipart(msg)
    
    for it in range(len(tasks)):
        msg = client.recv_multipart()
        print('msg:{}'.format(msg))

        msg[2] = b'END'
        client.send_multipart(msg)

    for task in tasks:
        task.join()
    
    client.close()
    ctx.term()


'''
输出结果为：

msg:[b'task0', b'', b'ready']
msg:[b'task1', b'', b'ready']
msg:[b'task0', b'', b'ready']
msg:[b'task1', b'', b'ready']
msg:[b'task0', b'', b'ready']
msg:[b'task1', b'', b'ready']
process 10
process 10
'''