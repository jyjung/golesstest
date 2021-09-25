import threading
import signal
from typing import List, Tuple, Dict, Optional
from enum import Enum, IntEnum , auto

class WorkingItem:
    def __init__(self,filename: str, id:str):
        self.filename = filename
        self.id = id
    def __str__(self) -> str:
        return "file[{file}]:id[{id}]".format(file=self.filename,id=self.id)


class ItemStore(object):
    def __init__(self, name: str):
        self.name = name
        self.cond = threading.Condition()
        self.items = []
        self.flag = True

    def loop(self):
        return self.flag
    
    def stop_loop(self):
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
                #If timeout  cond.wait  return False  
                b = self.cond.wait(timeout)
                if timeout and timeout > 0 and not b:
                    return []
            items, self.items = self.items, []
        return items


class PipeStore:
    def __init__(self, enumclass) -> None:
        signal.signal(signal.SIGINT,self.safe_exit)        
        signal.signal(signal.SIGTERM,self.safe_exit)
        self.len = len(enumclass)
        #self.stores = [ ItemStore() for _ in range(self.len)]
        self.stores= []
        self.idxmap = {}
        for idx , enum_item  in  enumerate(enumclass):
            self.stores.append(ItemStore(enum_item.name))
            self.idxmap[enum_item.name]= idx

    def safe_exit(self, signum, frame):
        print('safe_exit')
        self.stores[0].stop_loop()

    def get_store(self, enum_item) -> ItemStore:
        idx = self.idxmap[enum_item.name]
        if not 0 <= idx < self.len:
            raise ValueError
        return self.stores[idx]

    def get_next_store(self, enum_item) -> ItemStore:
        idx = self.idxmap[enum_item.name]
        next_idx = idx +1 
        if not 0 <= next_idx < self.len:
            raise ValueError
        return self.stores[next_idx]

def main():
    class MYOrder(Enum):
        FILE_ENCODING = 9
        FILE_UPLOAD = 7
        AAA = 6
        BBB = 19 
    
    mydict={}
    for i,j in enumerate(MYOrder):
        mydict[j.name] = i 

    print(mydict)
    
    
    a =WorkingItem('fff','bbb')
    print(a.filename)

def main2():
    #mylen = [1,2,3,4,5,6]        
    mylen = [1]        
    
    l1,l2 = mylen[0:1] , mylen[1:]
    print(l1)
    print(l2)
    
if __name__ == '__main__':
    main2()
