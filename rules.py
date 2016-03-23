#!/usr/bin/python


class Rule(object):
    def parse(self, line):
        raise NotImplemented


class AddScore(Rule):
    def parse(self, line):
        pass


class GameInfo(Rule):
    def parse(self, line):
        pass


class GameEnd(Rule):
    def parse(self, line):
        pass


class InvalidPassword(Rule):
    def parse(self, line):
        pass


class GameStat(Rule):
    def parse(self, line):
        pass


class PlayerInfo(Rule):
    def parse(self, line):
        pass


class MatchRequest(Rule):
    def parse(self, line):
        pass


class Connect(Rule):
    def parse(self, line):
        pass
