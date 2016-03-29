#!/usr/bin/python
import logging
import re
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
    invalid_password = 5
    game_info = 7
    game_end = 9
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


class Rule(object):
    def __init__(self, game):
        self.game = game

    def parse(self, line):
        logger.debug(line)


class Filter(Rule):
    def __init__(self, game=None):
        Rule.__init__(self, game)

    def parse(self, line):
        pass


class AddScore(Rule):
    pass


class GameInfo(Rule):
    pass


class GameEnd(Rule):
    def parse(self, line):
        pass


class InvalidPassword(Rule):
    def parse(self, line):
        pass


class GameStat(Rule):
    pass


class PlayerInfo(Rule):
    def __init__(self, game):
        Rule.__init__(self, game)
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
                logger.debug(raw[2])
                info['playing'] = int(raw[2])
            info['name'] = raw[3]
            info['idle'] = raw[4]
            info['rank'] = raw[5]
        except IndexError as e:
            # mostly corrupted data
            logger.error(e.message)

    def parse(self, line):
        if 'Info' in line and 'Rank' in line:
            return True
        if '******' in line:  # end parsing and flush result
            self.game.player_list = self.players
            return True

        # update self.game.player_list after finished
        result = re.search('27\s+(\S.*)', line)
        if result:
            raw_info = result.group(1).split("|")

            for raw in raw_info:
                info = self.load_raw_info(raw)
                if info:
                    self.players[info['name']] = info
        return True


class MatchRequest(Rule):
    pass


class Broadcast(Rule):
    def parse(self, line):
        pass


class Opponent(Rule):
    pass


class DataParser(object):
    rule_handlers = {}

    def __init__(self, game):
        self.game = game
        self.rule_handlers = {
            signum.add_score: AddScore(self.game),
            signum.info: Filter(),
            signum.broadcast: Broadcast(self.game),
            signum.game_info: GameInfo(self.game),
            signum.game_stat: GameStat(self.game),
            signum.match_request: MatchRequest(self.game),
            signum.player_info: PlayerInfo(self.game),
            signum.opponent: Opponent(self.game),
        }

    def parse(self, data):
        # logger.debug("start parsing")
        lines = data.splitlines()
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # logger.debug(line)
            try:
                indi = int(line[0:2])
            except ValueError:
                # Drop if the indicator is not a number
                continue
            for (signum, rule) in self.rule_handlers.items():
                if indi == signum:
                    rule.parse(line)
