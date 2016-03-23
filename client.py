#!/usr/bin/python

import sys
import threading
import asyncore
import json
from rule import DataParser
from go_socket import GoSocket


def empty(*args):
    sys.exit(0)


class Command():
    @staticmethod
    def authenticate(sock, context):
        user = context.get('user')
        password = context.get('password')
        if user:
            sock.buffer = user
            sock.handle_write()
        else:
            raise AttributeError('user not specified')
        # read here for test
        sock.handle_read()
        if password:
            sock.buffer = password
            sock.handle_write()
        # read here for test
        sock.handle_read()

    @staticmethod
    def list_games(sock, context):
        # send list games command
        command = ''
        if sock.writable():
            sock.buffer = command


class Client():
    def __init__(self, options=None):
        self.user = None
        self.password = None
        if options:
            self.context = options
        else:
            self.context = {
                'success': empty,
            }
        game = Game(self.user)
        self.context['game'] = game
        self.context['dataparser'] = DataParser(game)
        # TODO: add an option here to enable debug mode
        self.sock = GoSocket(self.context)

    def connect(self, options=None):
        if not options:
            options = {}
            options['success'] = empty
        kwargs = {'host': '210.155.158.200',
                  'port': 6969,
                  # 'fallback': self.listen
                  'callback': Command.authenticate,
                  'options': {'user': self.user,
                              'password': self.password,
                              },
                  }
        self.sock.connect(**kwargs)
        # self.input_thread.start()
        asyncore.loop()

    def disconnect(self):
        self.sock.disconnect()


class TestInput(threading.Thread):
    def __init__(self, go_socket):
        self.go_socket = go_socket
        threading.Thread.__init__(self)

    def run(self):
        pass


class RawInput(threading.Thread):
    def __init__(self, go_socket):
        self.go_socket = go_socket
        threading.Thread.__init__(self)

    def run(self):
        while True:
            send_data = raw_input()
            if send_data:
                self.go_socket.buffer = send_data


class Game(object):
    '''
    storing data
    '''
    def __init__(self, username):
        self.username = username
        self.inplay = False
        self.observer = {}  # game no., players name, ....
        self.komi = None
        self.handi = None
        self.board = []  # moves, captures, score, buf
        self.player_list = []
        self.game_list = []


if __name__ == '__main__':
    config = json.load(open("config.json"))
    cc = Client(config)
    cc.connect()
