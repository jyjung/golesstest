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


def fake_unzip_file(filenmae: str):
    return ['aaaa.docx', 'bbbb.docx', 'ccccc.docx']

def fake_sanitize_file(filename: str):
    return 

def file_unzip(filename: str) -> list : 
    mylist = fake_unzip_file(filename)
    #작업을 나누고 다시 합치는 부분을 구현한다.  
    return 

def file_zip(filelist: list) -> bool : 
    return True



def main():
    my_pipe = [
        file_unzip, 
        

    ]

    pl = PipeLine(my_pipe)
    pl.run()
    print('haha')
    for i in range(100):
        file = "file_" + str(i)
        pl.add(file)

    while pl.loop():
        time.sleep(1)




if __name__ == '__main__':
    main()



