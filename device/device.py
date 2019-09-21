#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import zmq
import time

ctx = zmq.Context.instance()
frontend = ctx.socket(zmq.PULL)
frontend.bind('tcp://127.0.0.1:5555')
backend = ctx.socket(zmq.PUSH)
backend.bind('tcp://127.0.0.1:5556')

zmq.proxy(frontend, backend)