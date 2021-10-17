import asyncio
import threading
import uuid
import time
from datetime import datetime
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
    FILE_RESIZE = 2
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

def base_step(ps : PipeStore, enum , sleep_time):
    store = ps.get_store(enum)
    next_store = ps.get_next_store(enum)    
    while store.loop():
        item = store.get_one(blocking=True,timeout=1)
        if item:
            print(enum.name,str(item))
            # item에다가 새로운 자료를 담는다. 
            time.sleep(sleep_time)
            if next_store:
                next_store.add(item)
    if next_store:     
        print(next_store.name,'loop exit')       
        next_store.stop_loop()



def file_download_step(ps : PipeStore):
    base_step(ps,ExecOrder.FILE_DOWNLOAD,1)

def file_sanitize_step(ps : PipeStore):
    base_step(ps,ExecOrder.FILE_SANITIZE,0.5)

def file_resize_step(ps : PipeStore):
    base_step(ps,ExecOrder.FILE_RESIZE,0.8)

    



def file_encoding_step(ps : PipeStore):
    working_item_list = []
    remain_item_list =[]
    store = ps.get_store(ExecOrder.FILE_ENCODING)
    next_store = ps.get_next_store(ExecOrder.FILE_ENCODING)
    while store.loop() or len(working_item_list) > 0:
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
        t.start()
    t2 = Thread(target=file_upload_step, args=(ps,))
    t2.start()

    t3 = Thread(target=file_download_step, args=(ps,))
    t3.start()

    t4 = Thread(target=file_sanitize_step, args=(ps,))
    t4.start()

    t5 = Thread(target=file_resize_step, args=(ps,))
    t5.start()



    store = ps.get_store(ExecOrder.FILE_DOWNLOAD)
    store.add('first1_file')
    store.add('first2_file')    
    store.add('first2_1_file')
    store.add('first2_2_file')
    store.add('first3_file')        
    while True:
        time.sleep(1)

main()
