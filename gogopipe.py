import threading
import time
import signal
from typing import List, Tuple, Dict, Optional, Union
from enum import Enum, IntEnum , auto


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

    def get_one(self, blocking=False , timeout=None ):
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


class PipeLine:
    def __init__(self, tasks) -> None:
        signal.signal(signal.SIGINT,self.safe_exit)        
        signal.signal(signal.SIGTERM,self.safe_exit)
        self.len = len(tasks)
        assert(self.len > 0)
        self.stores= []
        self.tasks = tasks
        self.thread_list = []
        self.libero_list = []
        self.loop_flag = True
        for idx , task  in  enumerate(tasks):
            self.stores.append(ItemStore(task.__name__))
        self.monitor()

    def add(self, item):
        self.stores[0].add(item)
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
        for t in self.libero_list:
            t.join()
        print('end libero')


    def loop_runner(self, idx , function):
        store = self.get_store(idx)
        next_store = self.get_next_store(idx)    
        store.inc()
        while store.is_loop():
            item = store.get_one(blocking=True,timeout=1)
            if item:
                next_item = function(item)
                if next_store:
                    next_store.add(next_item)
        store.dec()
        if next_store  and  store.store_count() == 0:     
            next_store.stop_loop()
        print(store.name, "exit")

    def once_runner(self, idx , function):
        store = self.get_store(idx)
        next_store = self.get_next_store(idx)    
        item = store.get_one(blocking=True,timeout=1)
        if item:
            next_item = function(item)
            if next_store:
                next_store.add(next_item)
        print(store.name,'!!!!!!!!!libero  do  this ')


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

    def run_libero(self): 
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
        LIBERO_COUNT = 5
        for idx , task  in enumerate(self.tasks):
            t = threading.Thread(target=self.loop_runner , args=(idx,task,))
            #t.daemon = True
            t.start()
            self.thread_list.append(t)

        for i in range(LIBERO_COUNT): 
            t = threading.Thread(target=self.run_libero)
            t.start()
            self.libero_list.append(t)


    
if __name__ == '__main__':
    aaa = 1

