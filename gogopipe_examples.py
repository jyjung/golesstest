import asyncio
import threading
import uuid
import time
import sys
from datetime import datetime
from threading import Thread
from queue import Queue
from enum import Enum, IntEnum ,auto
from typing import Union
from item_store import ItemStore , WorkingItem , PipeStore
from gogopipe import PipeLine
from typing import Any 
import signal
import logging

def file_download( filename: str) -> str:
    current_func_name = sys._getframe().f_code.co_name
    # print(current_func_name, filename)
    time.sleep(0.1)
    return filename

def file_sanitize(filename: str) -> str:
    current_func_name = sys._getframe().f_code.co_name
    # print(current_func_name, filename)

    time.sleep(0.1)
    return filename + "_sanitized"

def file_resize(filename: str) -> str:
    current_func_name = sys._getframe().f_code.co_name
    # print(current_func_name, filename)

    time.sleep(0.2)
    return filename + "_resized"

def file_encoding(filename: str) -> str:
    current_func_name = sys._getframe().f_code.co_name
    # print(current_func_name, filename)

    time.sleep(3)
    return filename + "_encoded"

def file_upload(filename : str) -> bool :
    current_func_name = sys._getframe().f_code.co_name
    # print(current_func_name, filename)
    return True

def main():
    logging.basicConfig(level=logging.DEBUG)
    file_task_pipe = [
        file_download,
        file_sanitize,
        file_resize,
        file_encoding,
        file_upload
    ]

    pl = PipeLine(file_task_pipe)
    pl.run()
    logging.debug("start")

    def signal_exit(signum, frame):
        logging.info('main exit')
        pl.safe_exit(signum, frame)
    
    signal.signal(signal.SIGINT,signal_exit)        
    signal.signal(signal.SIGTERM,signal_exit)

    for i in range(100):
        file = "file_" + str(i)
        pl.add(file)

    while pl.is_loop():
        time.sleep(1)

if __name__ == '__main__':
    main()
