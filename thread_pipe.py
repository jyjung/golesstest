import asyncio
import threading
import uuid
import time
from datetime import datetime
import gevent
import goless
from threading import Thread
from queue import Queue
from typing import Union
from item_store import ItemStore , WorkingItem
from expiringdict import ExpiringDict

cache_dict = ExpiringDict(max_len=1000, max_age_seconds=10)

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

def wait_until_complete(item_in: ItemStore, item_out: ItemStore):
    working_item_list = []
    remain_item_list =[]
    while True:
        inlist = item_in.get_all(blocking=False)
        new_item_list = [fake_file_encoding_start(v) for v in inlist]
        working_item_list = remain_item_list + new_item_list
        remain_item_list.clear()
        for item in working_item_list:
            # 실제 구현시 pending 되는것만 remain에다가 넣고 
            # 기타는 결과값을 확인한 후에 다시 집어 넣으면 된다. 
            if fake_file_encoding_status(item.id):
                item_out.add(item)
            else:
                remain_item_list.append(item)
        time.sleep(0.5)

def print_item(item_in: ItemStore):
    while True:
        inlist = item_in.get_all(blocking=True)
        for item in inlist:
            print('print_item',str(item))

def queue_test():
    q = ItemStore()
    q.add('aaa')
    q.add('bbb')
    q.add('ccc')
    print('1',q.get_all())
    print('2',q.get_all())

def pipe(item: ItemStore):
    while True:
        my = item.get_all(blocking=True)
        print('my',my)
        time.sleep(3)
    pass

def main():

    fd_in = ItemStore()
    fd_out = ItemStore()
    for i in range(2):
        t =Thread(target=wait_until_complete, args=(fd_in,fd_out,))
        t.daemon = True
        t.start()
    t2 = Thread(target=print_item, args=(fd_out,))
    t2.daemon = True
    t2.start()

    fd_in.add('first1_file')
    time.sleep(2)        
    fd_in.add('first2_file')    
    fd_in.add('first2_1_file')
    fd_in.add('first2_2_file')
    time.sleep(2)        
    fd_in.add('first3_file')        
    while True:
        time.sleep(1)

main()
