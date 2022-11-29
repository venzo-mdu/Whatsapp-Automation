# /home/user5/abdul/whatsappkit/env/lib/env/bin/python
import os
import subprocess

from waitress import serve
from main import app
from sys import platform,path
import requests

from paste.translogger import TransLogger
import logging
from threading import Thread
from time import sleep

# python_bin = "/home/user5/abdul/whatsappkit/env/bin/python3"

# # Path to the script that must run under the virtualenv
# script_file = "/home/user5/abdul/whatsappkit/env/bin/activate"

# s = subprocess.Popen([python_bin, script_file])
# print(s)

def flask_server():
    logger = logging.getLogger('waitress')
    logger.setLevel(logging.INFO)
    serve(TransLogger(app, setup_console_handler=False), host='127.0.0.1', port=5000)

def copyq_server():
    os.system("copyq")


def schedule_api():
    sleep(10)
    r = requests.get(url = 'http://127.0.0.1:5000/schedule')
    return r

if __name__ == "__main__":

    thread = Thread(target=flask_server)
    thread.start()
    if platform == "linux" or platform == "linux2":
        thread2 = Thread(target=copyq_server)
        thread2.start()
    r = schedule_api()
    print(r.json())