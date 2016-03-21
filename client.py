#!/usr/bin/python

import sys
import threading
import asyncore
import json
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
        self.user = 'zapbot'
        self.password = '12345'
        if options:
            self.context = options
        else:
            self.context = {
                'success': empty,
            }
        self.context['game'] = Game(self.user)
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


class RuleHandler(object):
    @staticmethod
    def parse(line):
        raise NotImplemented


class Game(object):
    '''
    storing data
    '''
    def __init__(self, username):
        self.username = username
        self.inplay = False
        self.board = []
        self.player_list = []
        self.game_list = []


class BoardUpdate(RuleHandler):
    @staticmethod
    def parse(line):
        pass


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


class DataParser(object):
    rule_handlers = []

    def __init__(self, options):
        self.context = options

    def parse(self, data):
        lines = data.splitlines()
        for line in lines:
            for rule in self.rule_handlers:
                rule.parse(line)


if __name__ == '__main__':
    config = json.load(open("config.json"))
    cc = Client(config)
    cc.connect()
