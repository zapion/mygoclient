#!/usr/bin/python

import asyncore
import socket
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s |%(name)s| %(message)s',
    filename='/tmp/mygoclient.log',
    filemode='a',
)
logger = logging.getLogger(__name__)
MAX_RECV = 8192


class signum():
    '''
    This class is mostly a memo for strange numbers
    '''

    info = 1  # '1 1' is prompt login, '1 5' connect info
    invalid_password = 5
    game_info = 7
    game_end = 9
    game_stat = 15
    stored_game = 18
    game_result = 20
    connect = 21
    add_score = 22
    opponent = 24
    player_info = 27
    undid = 28
    match_request = 36
    entry = 39
    adjourn = 48
    game_update = 49


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
        if kwargs.get('options'):
            options = kwargs.get('options')
        else:
            options = {}
        self.callback(self, options)

    def disconnect(self):
        self.send('quit\n')

    def run(self, options):
        if options.fallback:
            self.fallback = options.fallback
        self.fallback = empty
        if options.get('success'):
            self.handle_connect = options.get('success')

    def handle_connect(self):
        pass

    def handle_close(self):
        self.close()

    def writable(self):
        return (len(self.buffer) > 0)

    def handle_write(self):
        if self.buffer:
            if not self.buffer.endswith("\n"):
                self.buffer += "\n"
            sent = self.send(self.buffer)
            self.buffer = self.buffer[sent:]

    def handle_read(self):
        data = self.recv(MAX_RECV)
        logger.debug(data)
        if self.callback:
            self.callback(data)
        else:
            self.fallback()
