#!/usr/bin/python
import threading
import time
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s |%(name)s| %(message)s',
    filename='/tmp/mygoclient.log',
    filemode='a',
)
logger = logging.getLogger(__name__)


class InputThread(threading.Thread):
    '''
    Basic input thread
    @in: go client instance, within socket module
    @in: stop_event, a Thread.Event which supports set() & isSet()
    '''
    def __init__(self, go_client, stop_event):
        self.go_client = go_client
        self.sock = go_client.sock
        self.stop = stop_event
        threading.Thread.__init__(self)

    def run(self):
        pass

    def task(self):
        raise NotImplemented


class TestInput(InputThread):
    '''
    input source for command testing
    @in: go client instance, within socket module
    @in: stop_event, a Thread.Event which supports set() & isSet()
    @in: freq, how often it will fire in seconds
    '''
    def __init__(self, go_client, stop_event, freq=5):
        self.freq = freq
        InputThread.__init__(self, go_client, stop_event)

    def run(self):
        while not self.stop.isSet():
            self.task()
            time.sleep(self.freq)

    def task(self):
        logger.debug("who command fired")
        self.sock.buffer = "who"


class RawInput(TestInput):
    '''
    Use this module for interactive tracking
    '''
    def __init__(self, go_client, stop_event, freq=1):
        TestInput.__init__(self, go_client, stop_event, freq)

    def task(self):
        send_data = raw_input()
        if send_data:
            send_data = send_data.splitlines()[0]
            self.sock.buffer = send_data
