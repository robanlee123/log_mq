# -*- coding: utf-8 -*-
from __future__ import absolute_import

import logging
from logging import StreamHandler, Formatter

from msgpack import packb
import tailer
import zmq


## sanity check
try:
    HWM = zmq.HWM
except AttributeError:
    HWM = zmq.SNDHWM

class Log2MQ(object):

    def __init__(self, name='__log2mq__', config=None):
        config = config or {'endpoint': 'tcp://*:9999', 'logfile': '/dev/tty12'}
        self._init_logger(name)
        self._init_zmq(config['endpoint'])
        self.endpint = config['endpoint']
        self.logfile = config['logfile']


    def _init_logger(self, name):
        logger = logging.getLogger(name)
        handler = StreamHandler()
        formatter = Formatter("[%(asctime)s - %(levelname)-5s %(module)s:"
                          "%(lineno)s]: %(message)s")
        handler.setFormatter(formatter)
        handler.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        self.logger = logger

    def _init_zmq(self, endpoint):
        """initialize zmq endpoint"""
        context = zmq.Context()
        sock = context.socket(zmq.PUSH)
        sock.setsockopt(HWM, 10000)
        sock.setsockopt(zmq.LINGER, 0)
        sock.bind(endpoint)
        self.sock = sock

    def transfer(self):

        while True:
            try:
                for line in tailer.follow(self.logfile):
                    _ = line.strip()
                    if _:
                        self.sock.send(packb(_))
            except KeyboardInterrupt:
                sock.close()
                self.logger.info('SIGINT detected')
                return
            except:
                from traceback import format_exc
                self.logger.error("{0}{1}".format("\n", format_exc()))
