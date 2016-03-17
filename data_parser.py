#!/usr/bin/python
import re


class DataParser(object):

    def append_data(self, data):
        next = None
        if not self.data:
            self.data = ''
        self.data += data
        if re.match('[\w\W]*#>[\w\W]*'):
            self.call_parser()
        else:
            next = self.append_data
        return next

    def call_parser(self):
        self.parse(self.data)

    def parse(self, data):
        raise NotImplemented
