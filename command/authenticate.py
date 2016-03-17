#!/usr/bin/python
import re


def empty():
    pass


class Authenticate(object):
    def __init__(self, socket, context):
        self.socket = socket
        self.context = context

    def run(self, options):
        if options.success is None:
            self.on_auth_success = empty
        else:
            self.on_auth_success = options.success
        self.login = options.login
        self.password = options.password
        self.socket.send(self.password)
        return self.on_prompt_login

    def on_prompt_login(self):
        self.socket.send(self.login)
        return self.on_prompt_password

    def on_prompt_password(self, data):
        next = None
        if re.match('/Password:/', data):
            self.socket.send(self.password)
            next = self.check_password
        return next

    def check_password(self, data):
        if re.search('You have entered IGS', data):
            return self.on_auth_success
