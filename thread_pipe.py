import asyncio
import threading
import uuid
import time
from datetime import datetime
import gevent
import goless
from threading import Thread
from queue import Queue
from enum import Enum, IntEnum ,auto
from typing import Union
from item_store import ItemStore , WorkingItem , PipeStore
from expiringdict import ExpiringDict

cache_dict = ExpiringDict(max_len=1000, max_age_seconds=10)

class ExecOrder(Enum):
    FILE_DOWNLOAD =0
    FILE_SANITIZE = 1
    FILE_CHANGESIZE = 2
    FILE_ENCODING = 3
    FILE_UPLOAD = 4

def fake_file_download()-> str:
    id = str(uuid.uuid4()) + ".docx"
    time.sleep(0.4)
    return id

def fake_file_upload(filename: str):
    time.sleep(0.5)

def fake_file_encoding_start(filename: str)-> str:
    id = str(uuid.uuid4())
    cache_dict[id] = time.time()

    return WorkingItem(filename,id)

def fake_file_encoding_status( id: str)-> bool:
    if id in cache_dict  and  time.time() - cache_dict[id] > 2:
        return True
    else:
        return False

def file_download_step(ps : PipeStore):
    store = ps.get_store(ExecOrder.FILE_DOWNLOAD)
    next_store = ps.get_next_store(ExecOrder.FILE_DOWNLOAD)    
    while store.loop():
        inlist = store.get_all(blocking=True,timeout=1)
        for item in inlist:
            print('download_item',str(item))

    



def file_encoding_step(ps : PipeStore):
    working_item_list = []
    remain_item_list =[]
    store = ps.get_store(ExecOrder.FILE_ENCODING)
    next_store = ps.get_next_store(ExecOrder.FILE_ENCODING)
    while store.loop():
        inlist = store.get_all(blocking=False)
        new_item_list = [fake_file_encoding_start(v) for v in inlist]
        working_item_list = remain_item_list + new_item_list
        remain_item_list.clear()
        for item in working_item_list:
            # 실제 구현시 pending 되는것만 remain에다가 넣고 
            # 기타는 결과값을 확인한 후에 다시 집어 넣으면 된다. 
            if fake_file_encoding_status(item.id):
                # 다음 처리를 위한 저장소로 넘겨준다  
                next_store.add(item)
            else:
                remain_item_list.append(item)
        time.sleep(0.5)
    next_store.stop_loop()
    print('file encoding end')
    

def file_upload_step(ps: PipeStore):
    store = ps.get_store(ExecOrder.FILE_UPLOAD)
    while store.loop():
        inlist = store.get_all(blocking=True,timeout=3)
        for item in inlist:
            print('print_item',str(item))
    print('file upload end')
        
    # exit next step

def queue_test():
    q = ItemStore()
    q.add('aaa')
    q.add('bbb')
    q.add('ccc')
    print('1',q.get_all())
    print('2',q.get_all())


def main():
    ps = PipeStore(ExecOrder)
    for i in range(2):
        t =Thread(target=file_encoding_step, args=(ps,))
        t.daemon = True
        t.start()
    t2 = Thread(target=file_upload_step, args=(ps,))
    t2.daemon = True
    t2.start()

    store = ps.get_store(ExecOrder.FILE_ENCODING)
    store.add('first1_file')
    time.sleep(2)        
    store.add('first2_file')    
    store.add('first2_1_file')
    store.add('first2_2_file')
    time.sleep(2)        
    store.add('first3_file')        
    while True:
        time.sleep(1)

main()
