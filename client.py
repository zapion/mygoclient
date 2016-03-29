#!/usr/bin/python


import sys
import threading
import asyncore
import json
import logging
from rules import DataParser
from go_socket import GoSocket
# from robot import TestInput
from robot import RawInput


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s |%(name)s| %(message)s',
    filename='/tmp/mygoclient.log',
    filemode='a',
)
logger = logging.getLogger(__name__)


def empty(*args):
    sys.exit(0)


class Command():
    # reference:
    # who, games, observe, chatter(chat in game room),
    # kibitz(comment in game room[recorded]), tell, shout, stats,
    #      rank, match, coords, toggle
    # TODO: move this class to a file

    @staticmethod
    def stats(sock, context):
        '''
        @in: playername: if not specified, query self stat
        '''
        cmd = 'stats'
        if 'playername' in context:
            cmd += context.get('playername')
        sock.buffer = cmd

    @staticmethod
    def authenticate(sock, context):
        user = context.get('user')
        password = context.get('password')
        if user:
            sock.buffer = user
            sock.handle_write()
        else:
            raise AttributeError('user not specified')
        if password:
            sock.buffer = password
            sock.handle_write()
        # sock.callback = context.get('callback')

    @staticmethod
    def list_games(sock, context):
        # send list games command
        command = 'games'
        sock.buffer = command

    @staticmethod
    def list_players(sock, context):
        # send list games command
        command = 'who'
        sock.buffer = command


class Client():
    def __init__(self, options=None):
        self.expired = threading.Timer(1000, self.expire_handler)
        self.expired.start()
        self.user = options.get('user')
        self.password = options.get('password')
        self.keep_alive = True
        if 'keep_alive' in options:
            self.keep_alive = options.get('keep_alive')
        if options:
            self.context = options
        else:
            self.context = {
                'success': empty,
            }
        game = Game(self.user)
        self.context['game'] = game
        self.parser = DataParser(game)
        # TODO: add an option here to enable debug mode
        self.context['callback'] = self.parser.parse
        self.sock = GoSocket(self.context)

    def expire_handler(self):
        if self.keep_alive:
            self.expired.cancel()
            self.expired = threading.Timer(1000, self.expire_handler)
            self.expired.start()
        else:
            self.disconnect()

    def connect(self, options=None):
        if not options:
            options = {}
            options['success'] = empty
        kwargs = {'host': '210.155.158.200',
                  'port': 6969,
                  'callback': Command.authenticate,
                  'options': {'user': self.user,
                              'password': self.password,
                              # 'callback': self.parser.parse
                              },
                  }
        self.sock.connect(**kwargs)
        logger.info('connection setup successfully')

    def disconnect(self):
        self.sock.disconnect()

    def command(self, name, context=None):
        Command.__dict__.get(name).__func__(self.sock, context)


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
        self.board = []  # moves, captures, score, ...
        self.player_list = {}
        self.game_list = {}


if __name__ == '__main__':
    stop_event = threading.Event()
    config = json.load(open("config.json"))
    cc = Client(config)
    bot = RawInput(go_client=cc, stop_event=stop_event)
    try:
        cc.connect()
        bot.start()
        asyncore.loop()
    except KeyboardInterrupt:
        stop_event.set()
