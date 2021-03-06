from random import sample, randint
from string import ascii_letters
from time import localtime, asctime, sleep
from datetime import datetime
from os import environ
import os
import logging
import json

from kivy.logger import Logger
from kivy.utils import platform
from android import activity

from oscpy.server import OSCThreadServer
from oscpy.client import OSCClient

CLIENT = OSCClient('localhost', 3002)
stopped = False
broadcast_receiver = None
pending_alarm = False

if platform == 'android':
    from jnius import autoclass
    from android import mActivity
    PythonService = autoclass('org.kivy.android.PythonService')
    PythonService.mService.setAutoRestartService(True)


def send_date():
    'send date to the application'
    CLIENT.send_message(
        b'/date',
        [asctime(localtime()).encode('utf8'), ],
    )


def stop_service():
    if platform == 'android':
        PythonService.mService.setAutoRestartService(False)
    global stopped
    stopped = True


if __name__ == '__main__':
    argument = environ.get('PYTHON_SERVICE_ARGUMENT', 'null')
    argument = json.loads(argument) if argument else None
    argument = {} if argument is None else argument
    logging.info('argument=%r', argument)
    try:
        SERVER = OSCThreadServer()
        SERVER.listen('localhost', port=3000, default=True)
        SERVER.bind(b'/stop_service', stop_service)
        while True:
            sleep(1)
            send_date()
            if stopped:
                break
        SERVER.terminate_server()
        sleep(0.1)
        SERVER.close()
    except Exception as e:
        logging.exception(e)
