import threading
import time
import signal
import uuid
from typing import List, Tuple, Dict, Optional, Union, Callable, Any
from enum import Enum, IntEnum , auto

SPLIT_TYPE = 'split'
MERGE_TYPE = 'merge'

def split(func , **kwargs) -> Tuple[Dict, Callable]:
    info = {
        '_type': SPLIT_TYPE,
    }
    for key, value in kwargs.items():
        info[key] = value
    return (info , func)

def merge(func, **kwargs) -> Tuple[Dict, Callable]:
    info = {
        '_type': MERGE_TYPE,
    }
    for key, value in kwargs.items():
        info[key] = value
    return (info , func)


class ItemStore(object):
    def __init__(self, name: str):
        self.name = name
        self.cond = threading.Condition()
        self.lock = threading.Lock()
        self.items = []
        self.flag = True
        self.counter =0

    def inc(self,d=1):
        with self.lock:
            self.counter += d
    def dec(self,d=-1):
        self.inc(d)

    def store_count(self):
        with self.lock:
            return self.counter

    def item_count(self): 
        with self.cond:
            return len(self.items)

    def is_loop(self):
        with self.lock:
            return self.flag

    def loop(self):
        with self.lock:
            return self.flag
    def stop_loop(self):
        with self.lock:
            self.flag = False

    def add(self, item):
        with self.cond:
            self.items.append(item)
            self.cond.notify() # Wake 1 thread waiting on cond (if any)

    def get_one(self, blocking=False , timeout=None ) -> Tuple[Dict,Any]:
        with self.cond:
            while blocking and len(self.items) == 0:
                b = self.cond.wait(timeout)
                if timeout and timeout > 0 and not b:
                    return None
            item, self.items = self.items[0], self.items[1:]
        return item

    def get_all(self, blocking=False , timeout=None ):
        with self.cond:
            # If blocking is true, always return at least 1 item
            while blocking and len(self.items) == 0:
                #If timeout occure...   cond.wait  return False  
                b = self.cond.wait(timeout)
                if timeout and timeout > 0 and not b:
                    return []
            items, self.items = self.items, []
        return items

def get_function_name( pipe_item: Union[tuple,Callable]) -> str:
    if isinstance(pipe_item, tuple):
        return pipe_item[1].__name__
    else:
        return pipe_item.__name__


class PipeLine:
    def __init__(self, tasks) -> None:
        signal.signal(signal.SIGINT,self.safe_exit)        
        signal.signal(signal.SIGTERM,self.safe_exit)
        self.len = len(tasks)
        assert(self.len > 0)
        self.stores= []
        self.tasks = tasks
        self.thread_list = []
        self.extra_thread_list = []
        self.loop_flag = True
        for idx , task  in  enumerate(tasks):
            self.stores.append(ItemStore(get_function_name(task)))
        self.monitor()

    def add(self, item):
        tag = {
            'id': str(uuid.uuid4())
        }
        self.stores[0].add((tag, item))
    def is_loop(self):
        return self.loop_flag
    def loop(self):
        return self.loop_flag

    def safe_exit(self, signum, frame):
        print('safe_exit')
        self.stores[0].stop_loop()
        for t in self.thread_list:
            t.join()
        self.loop_flag = False
        for t in self.extra_thread_list:
            t.join()
        print('end extra thread')

    def base_runner(self, idx, cbfunction):
        store = self.get_store(idx)
        next_store = self.get_next_store(idx)    
        store.inc()
        while store.is_loop():
            cbfunction(store, next_store)
        store.dec()
        if next_store  and  store.store_count() == 0:     
            next_store.stop_loop()
        print(store.name, "exit")


    def one_to_one_runner(self, idx , function):
        def _inner(store, next_store):
            item = store.get_one(blocking=True,timeout=1)
            
            if item:
                next_item = function(item[1])
                if next_store:
                    next_store.add((item[0], next_item))
        self.base_runner(idx,_inner)

    def one_to_split_runner(self, idx , function ,tag):
        def _inner(store, next_store):
            item = store.get_one(blocking=True,timeout=1)
            if item:
                next_items = function(item[1])
                items_count = len(next_items)
                if next_store:
                    for idx,item in enumerate(next_items):
                        tag = {
                            '_count': items_count,
                            '_idx' : idx
                        }
                        #todo  item[0] Dict 와 머지후에 next store로 넘겨준다.  

                        next_store.add((item)
        self.base_runner(idx,_inner)

    def merge_to_one_runner(self, idx , function , tag):
        def _inner(store, next_store):
            item = store.get_one(blocking=True,timeout=1)
            if item:
                next_item = function(item)
                if next_store:
                    next_store.add(next_item)
        self.base_runner(idx,_inner)


        # store = self.get_store(idx)
        # next_store = self.get_next_store(idx)    
        # store.inc()
        # while store.is_loop():
        #     item = store.get_one(blocking=True,timeout=1)
        #     if item:
        #         next_item = function(item)
        #         if next_store:
        #             next_store.add(next_item)
        # store.dec()
        # if next_store  and  store.store_count() == 0:     
        #     next_store.stop_loop()
        # print(store.name, "exit")

    def once_runner(self, idx , function):
        store = self.get_store(idx)
        next_store = self.get_next_store(idx)    
        tuple_item = store.get_one(blocking=True,timeout=1)
        if tuple_item:
            next_item = function(tuple_item[1])
            if next_store:
                next_store.add((tuple_item[0],next_item))
        print(store.name,'<--- Extra Thread  do  this task')


    def get_store(self, idx) -> ItemStore:
        if not 0 <= idx < self.len:
            raise ValueError
        return self.stores[idx]

    def get_next_store(self, idx) -> Union[ItemStore,None]:
        next_idx = idx +1 
        if next_idx >= self.len:
            return None
        elif not 0 <= next_idx < self.len:
            raise ValueError
        return self.stores[next_idx]

    def monitor(self):
        def _inner():
            while self.loop_flag:
                time.sleep(5)
                print('-' * 40)
                for store in self.stores:
                    print(store.name, store.item_count())
        t = threading.Thread(target=_inner )
        t.daemon = True
        t.start()

    def run_extra_thread(self): 
        def get_busy_store(): 
            for idx, store in enumerate(self.stores):
                if store.item_count() > 1:
                    return True,idx
            return False,0

        while self.loop_flag:
            busy , idx = get_busy_store()
            if not busy:
                time.sleep(0.5)
            else:
                self.once_runner(idx,self.tasks[idx])
    
    def run(self):
        EXTRA_THREAD_COUNT = 5
        for idx , task  in enumerate(self.tasks):
            if isinstance(task, tuple):
                if task[0]['_type'] == SPLIT_TYPE:
                    t = threading.Thread(target=self.one_to_split_runner, args =(idx,task[1],task[0]['tag'],))
                elif task[0]['_type'] == MERGE_TYPE:
                    t = threading.Thread(target=self.merge_to_one_runner, args =(idx,task[1],task[0]['tag'],))
            else:
                t = threading.Thread(target=self.one_to_one_runner , args=(idx,task,))
            t.start()
            self.thread_list.append(t)

        for i in range(EXTRA_THREAD_COUNT): 
            t = threading.Thread(target=self.run_extra_thread)
            t.start()
            self.extra_thread_list.append(t)
    
if __name__ == '__main__':
    aaa = 1

