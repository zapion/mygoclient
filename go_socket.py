#!/usr/bin/python

import asyncore
import socket


def empty():
    pass


class GoSocket(asyncore.dispatcher):
    def __init__(self, context):
        self.context = context
        self.callback = empty
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, kwargs):
        if kwargs['fallback']:
            self.fallback = kwargs['fallback']
        else:
            self.fallback = empty
        asyncore.dispatcher.connect(self, kwargs['host'], kwargs['port'])

    def run(self, options):
        if options.fallback:
            self.fallback = options.fallback
        self.fallback = empty
        if options.success:
            self.handle_connect = options.success
        self.connect
