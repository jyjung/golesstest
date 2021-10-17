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


def fake_unzip_file(filenmae: str):
    return ['aaaa.docx', 'bbbb.docx', 'ccccc.docx']

def fake_sanitize_file(filename: str):
    return filename

def file_unzip(filename: str) -> list : 
    mylist = fake_unzip_file(filename)
    #작업을 나누고 다시 합치는 부분을 구현한다.  
    return mylist

def file_zip(filelist: list) -> bool : 
    return "aaa.zip"



def main():
    my_pipe = [
        split("zip",file_unzip),
        fake_sanitize_file, 
        merge("zip",file_zip)
 
    ]

    pl = PipeLine(my_pipe)
    pl.run()
    print('haha')
    for i in range(2):
        file = "file_" + str(i)
        pl.add(file)

    while pl.loop():
        time.sleep(1)

def get_function_name( tuple_of_func):
    if isinstance(tuple_of_func, tuple):
        return tuple_of_func[1].__name__
    else:
        return tuple_of_func.__name__

def test():
    a = ("dfwefwe",file_zip)
    print(get_function_name(a))
    print(get_function_name(file_zip))
    print(get_function_name(file_unzip))
 

if __name__ == '__main__':
    main()
    #test()



