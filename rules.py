#!/usr/bin/python
import logging
import re
import threading
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s |%(name)s| %(message)s',
    filename='/tmp/mygoclient.log',
    filemode='a',
)
logger = logging.getLogger(__name__)


class signum():
    '''
    This class is mostly a memo for strange numbers
    '''
    info = 1  # '1 1' is prompt login, '1 5' connect info
    alert = 5
    game_info = 7
    help_str = 8
    system_message = 9
    game_stat = 15
    stored_game = 18
    game_result = 20
    broadcast = 21
    add_score = 22
    opponent = 24
    player_info = 27
    undid = 28
    match_request = 36
    entry = 39
    adjourn = 48
    game_update = 49


class Parser(object):
    def __init__(self, data_store, callback=None):
        self.data_store = data_store
        self.callback = callback

    def parse(self, line):
        logger.debug("rule:" + line)


class Filter(Parser):
    def __init__(self, data_store=None):
        Parser.__init__(self, data_store)

    def parse(self, line):
        pass


class AddScore(Parser):
    pass


class Entry(Parser):
    def parse(self, line):
        if "IGS" in line:
            # Do setup for IGS
            self.callback()


class GameInfo(Parser):
    def __init__(self, data_store):
        self.timer = None
        self.game_list = {}
        Parser.__init__(self, data_store)

    def parse(self, line):
        game_info = {}
        if '###' in line:
            self.timer = threading.Timer(15, self.summary)
            self.timer.daemon = True
            self.timer.start()
            return
        line = line[2:]
        result = re.search('\[ *([0-9]+)\]\s+(\S*)\s+\[(.*)\] vs', line)
        try:
            game_info['no.'] = result.group(1)
            game_info['white'] = {'name': result.group(2),
                                  'rank': result.group(3),
                                  }
            pattern = 'vs\.\s+(\S+) \[ *([^\]]*)\] \(([^\)]*)\) \((.*)\)'
            result = re.search(pattern, line)
            game_info['white'] = {'name': result.group(1),
                                  'rank': result.group(2),
                                  }
            raw_info = filter(lambda x: x, result.group(3).split(" "))
            game_info['move'] = int(raw_info[0])
            game_info['size'] = int(raw_info[1])
            game_info['handicap'] = int(raw_info[2])
            game_info['komi'] = float(raw_info[3])
            game_info['BY'] = raw_info[4]
            game_info['FR'] = raw_info[5]
            game_info['observer'] = int(result.group(4))
            self.game_list[game_info['no.']] = game_info
        except:
            logger.error("fail when parsing: " + line)

    def summary(self):
        self.data_store.game_list = self.game_list
        logger.debug("game no.: {}".format(len(self.data_store.game_list)))
        self.game_list = {}
        if self.timer:
            self.timer.cancel()
        self.timer = None
        return True


class SystemMessage(Parser):
    def parse(self, line):
        pass


class Alert(Parser):
    def parse(self, line):
        logger.debug(line)
        raw_info = filter(lambda x: x, line.split(" "))
        raw_info.pop(0)
        if 'request:' == raw_info[1]:
            request = {}
            request['name'] = raw_info[0]


class GameStat(Parser):
    pass


class PlayerInfo(Parser):
    def __init__(self, data_store):
        Parser.__init__(self, data_store)
        self.players = {}

    def load_raw_info(self, raw):
        info = {}
        raw = filter(lambda x: x, raw.split(' '))
        if len(raw) < 5:
            # remove dummy player
            return None
        result = re.search('.*(--|[0-9]+)', raw[0])
        if result:
            raw.insert(1, result.group(1))
        try:
            opts = raw[0]
            if 'Q' in opts:
                info['quiet'] = True
            if 'S' in opts:
                info['noshout'] = True
            if 'X' in opts:
                info['closed'] = True
            if '!' in opts:
                info['searching'] = True
            if '--' not in raw[1]:
                info['observing'] = int(raw[1])
            if '--' not in raw[2]:
                info['playing'] = int(raw[2])
            info['name'] = raw[3]
            info['idle'] = raw[4]
            info['rank'] = raw[5]
            return info
        except IndexError as e:
            # mostly corrupted data
            logger.error(e.message)

    def parse(self, line):
        if 'Info' in line and 'Rank' in line:
            return True
        if '******' in line:  # end parsing and flush result
            self.data_store.player_list = self.players
            logger.debug("player no.:{}".format(len(self.players)))
            logger.debug("in data: {}".format(len(self.data_store.player_list)))
            return True

        # update self.data_store.player_list after finished
        result = re.search('27\s+(\S.*)', line)
        if result:
            raw_info = result.group(1).split("|")

            for raw in raw_info:
                info = self.load_raw_info(raw)
                if info:
                    self.players[info['name']] = info
        return True


class MatchRequest(Parser):
    pass


class Broadcast(Parser):
    def parse(self, line):
        pass


class Opponent(Parser):
    pass


class DataParser(object):

    def __init__(self, data_store):
        self.data_store = data_store

    def set_handlers(self, handlers):
        self.parsers = {
            signum.add_score: AddScore(self.data_store),
            signum.info: Filter(),
            signum.alert: Alert(self.data_store, handlers.alert_handler),
            signum.system_message: SystemMessage(self.data_store),
            signum.broadcast: Broadcast(self.data_store),
            signum.game_info: GameInfo(self.data_store),
            signum.game_stat: GameStat(self.data_store),
            signum.match_request: MatchRequest(self.data_store),
            signum.player_info: PlayerInfo(self.data_store),
            signum.opponent: Opponent(self.data_store),
            signum.entry: Entry(self.data_store, handlers.entry_handler),
        }

    def parse(self, data):
        lines = data.splitlines()
        for line in lines:
            try:
                indi = int(line[0:2])
            except ValueError:
                logger.error("Failed to load: " + line)
                indi = 1
            # Drop if the indicator is not a number
            line = line.strip()
            if not line:
                continue
            for (num, parser) in self.parsers.items():
                if indi == num:
                    parser.parse(line)


class EventHandler(object):

    def __init__(self, sock):
        self.sock = sock

    def alert_handler(self, line):
        pass

    def entry_handler(self):
        '''
        deal with IGS setup merely
        will add if more server supported
        '''
        logger.debug("triggering entry handler")
        sock = self.sock
        sock.buffer = "id pythgo 0.0.1\n"
        sock.buffer = "toggle newrating\n"
        sock.buffer = "toggle nmatch true\n"
        # send default nmatch range
        sock.buffer = "nmatchrange BWN 0-9 19-19 60-60 60-3600 25-25 0 0 0-0"
