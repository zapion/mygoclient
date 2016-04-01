#!/usr/bin/python


import sys
import threading
import asyncore
import json
import logging
from rules import DataParser
from rules import EventHandler
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
    def decline(sock, opponent):
        sock.buffer += "decline {}".format(opponent)

    @staticmethod
    def accept_nmatch(sock, context):
        opponent, condition = context['opponent'], context['condition']
        sock.buffer += "nmatch {} {}".format(opponent, condition)

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
        data = sock.recv(8192)
        logger.debug(data)
        user = context.get('user')
        password = context.get('password')
        # read welcome message
        if user:
            sock.buffer = user
            sock.handle_write()
        else:
            raise AttributeError('user not specified')
        if password:
            sock.buffer = password
            sock.handle_write()
            try:
                data = sock.recv(8192)
                logger.debug(data)
            except:
                pass

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
        # FIXME: temporarily remove keep alive, it causes raw_input can't
        # stop gracefully
        # self.expired = threading.Timer(1000, self.expire_handler)
        # self.expired.daemon = True
        # self.expired.start()
        self.user = options.get('user')
        self.password = options.get('password')
        # self.keep_alive = True
        # if 'keep_alive' in options:
        #     self.keep_alive = options.get('keep_alive')
        if options:
            self.context = options
        else:
            self.context = {
                'success': empty,
            }
        data_store = DataStore(self.user)
        self.data_store = data_store
        self.context['datastore'] = data_store
        self.parser = DataParser(data_store)
        self.context['callback'] = self.parser.parse
        self.sock = GoSocket(self.context)
        self.event_handlers = EventHandler(self.sock)
        self.parser.set_handlers(self.event_handlers)
        # TODO: add an option here to enable debug mode

    def __del__(self):
        del self.event_handlers

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
                              },
                  }
        self.sock.connect(**kwargs)
        logger.info('connection setup successfully')

    def disconnect(self):
        self.sock.disconnect()

    def command(self, name, context=None):
        Command.__dict__.get(name).__func__(self.sock, context)


class DataStore(object):
    '''
    storing data
    '''
    def __init__(self, username):
        self.nmatch_request = []
        self.username = username
        self.inplay = False
        self.observe = {}  # game no., players name, ....
        self.komi = None
        self.handi = None
        self.play = {}  # moves, captures, score, ...
        self.player_list = {}
        self.game_list = {}


if __name__ == '__main__':
    stop_event = threading.Event()
    config = json.load(open("config.json"))
    cc = Client(config)
    bot = RawInput(go_client=cc, stop_event=stop_event)
    bot.daemon = True
    try:
        cc.connect()
        bot.start()
        asyncore.loop(timeout=0.1)
    except KeyboardInterrupt:
        stop_event.set()
        cc.disconnect()
