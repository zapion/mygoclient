#!/usr/bin/python

import asyncore
import socket
import logging
import errno

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s |%(name)s| %(message)s',
    filename='/tmp/mygoclient.log',
    filemode='a',
)
logger = logging.getLogger(__name__)
MAX_RECV = 8192


def empty(*args):
    pass


class GoSocket(asyncore.dispatcher):
    def __init__(self, context):
        asyncore.dispatcher.__init__(self)
        self.context = context
        if context.get('callback'):
            self.callback = context.get('callback')
        self.buffer = ""
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, **kwargs):
        if kwargs.get('fallback'):
            self.fallback = kwargs['fallback']
        else:
            self.fallback = empty
        host = kwargs['host']
        port = kwargs['port']
        logger.info("connect to [{0}:{1}]".format(host, port))
        asyncore.dispatcher.connect(self, (host, port))
        self.connect_kwargs = kwargs

    def disconnect(self):
        self.send('quit\n')

    def handle_connect(self):
        kwargs = self.connect_kwargs
        if kwargs.get('options'):
            options = kwargs.get('options')
        else:
            options = {}
        kwargs['callback'](self, options)

    def handle_close(self):
        logger.info("connection closed")

    def writable(self):
        return (len(self.buffer) > 0)

    def handle_write(self):
        if self.buffer:
            if not self.buffer.endswith("\n"):
                self.buffer += "\n"
            sent = self.send(self.buffer)
            self.buffer = self.buffer[sent:]

    def handle_read(self):
        data = ''
        try:
            data = self.recv(MAX_RECV)
        except socket.error as e:
            # [Errno 35] Resource temporarily unavailable.
            if e.errno == errno.EAGAIN:
                # Means nothing to read, catch it on osx mostly
                pass
        if data:
            if self.__dict__.get('callback'):
                self.callback(data)
            elif self.__dict__.get('fallback'):
                self.fallback()
