#!/usr/bin/python
import logging
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
    def parse(self, line):
        logger.debug(line)


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
