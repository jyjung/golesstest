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
from gogopipe import PipeLine , split , merge
from typing import Any 
import functools
import logging
logging.basicConfig(level=logging.DEBUG)


def fake_unzip_file(filename: str):
    return [ filename[:-4] + v for v in ["aaa","bbb","ccc"] ]
    

def fake_sanitize_file(filename: str):
    time.sleep(1)
    #logging.debug('sanitize: ' + filename)
    return filename

def file_unzip(filename: str) -> list : 
    #logging.debug('unzip: ' + filename)
    time.sleep(1)
    mylist = fake_unzip_file(filename)
    #작업을 나누고 다시 합치는 부분을 구현한다.  
    return mylist

def file_zip(filelist: list) -> bool :
    logging.debug('zip!!!: ' + str(filelist))

    time.sleep(1) 
    return "aaa.zip"

def file_after(filename: str) -> bool :
    return "hhhhh.zip"

def main():
    my_pipe = [
        split(file_unzip),
        fake_sanitize_file, 
        merge(file_zip),
        file_after
 
    ]

    pl = PipeLine(my_pipe)
    pl.run()
    for i in range(3):
        file = "file_" + str(i)+ ".zip"
        pl.add(file)

    while pl.loop():
        time.sleep(1)


 

if __name__ == '__main__':
    main()
    #test()



