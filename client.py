#!/usr/bin/python
from go_socket import GoSocket
from commands.authenticate import Authenticate
from commands.listgames import ListGames
from commands.requestmatch import RequestMatch
from commands.acceptmatchrequest import AcceptMatchRequest
from commands.listplayers import ListPlayers
from commands.play import Play
from listeners.matchrequest import MatchRequest
from listeners.boardupdate import BoardUpdate


command_list = {
    'authenticate': Authenticate,
    'listgames': ListGames,
    'requestmatch': RequestMatch,
    'acceptmatchrequest': AcceptMatchRequest,
    'listplayers': ListPlayers,
    'play': Play,
}

listener_list = {
    'matchrequest': MatchRequest,
    'boardupdate': BoardUpdate,
}


def empty():
    pass


class Client():
    def __init__(self, options):
        self.add_all_commands()
        if options:
            self.context = options
        else:
            self.context = {}
        # TODO: add an option here to enable debug mode
        self.sock = GoSocket()

    def connect(self, options):
        self.authenticate(options)
        kwargs = {'host': '210.155.158.200',
                  'port': 6969,
                  'fallback': self.listen}
        self.sock.connect(**kwargs)

    def disconnect(self):
        self.sock.disconnect()

    def listen(self, data):
        for lstn_name, lstn_type in listener_list.items():
            listener = lstn_type(self.sock, self.context)
            if listener.parse(data):
                listener.run()
                break

    def add_command(self, command):
        name = command[0]
        instance = command[1](self.sock, self.context)
        setattr(self, name, instance)
        callback = instance.run(self.context)
        if not callback:
            callback = self.listen

    def add_all_commands(self):
        for item in command_list.items():
            self.add_command(item)
