#!/usr/bin/python
import re


class BoardParser():
    def __init__(self, data):
        self.data = data
        self.board = {'matrix': []}

    def get_row_pattern(self, row):
        pass
        # str_pattern

    def filter_data(self):
        # letter_line = ''
        # code = ''
        # splitted_data = ''
        for col in range(1, self.size):
            pass

    def compute_size(self):
        if re.search('19|', self.data):
            self.size = 19
        elif re.search('13|', self.data):
            self.size = 13
        else:
            self.size = 9

    def parse(self):
        # match_object = None
        self.compute_size()
        self.filter_data()
        for row in range(1, self.size + 1):
            pass
            # match_object = re.match('', )
