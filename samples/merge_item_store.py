import threading
import time
from expiringdict import ExpiringDict


class ItemStore(object):
    def __init__(self, name: str):
        self.name = name
        self.cond = threading.Condition()
        self.lock = threading.Lock()
        self.items = []
        self.cache = ExpiringDict(max_len=1000, max_age_seconds=180)
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

    def stop_loop(self):
        with self.lock:
            self.flag = False

    def add_splitted(self,tag,item):
        id = tag['id']
        count = tag['count']
        with self.cond:
            if id in self.cache:
                self.cache[id].append(item)
            else:
                self.cache[id] = [item]
            if count == len(self.cache[id]):
                self.items.append(self.cache.pop(id,None))
                self.cond.notify()

    def get_splitted(self,tag, blocking=False , timeout=None):
        with self.cond:
            while blocking:
                b = self.cond.wait(timeout)
                if timeout and timeout > 0 and not b:
                    return None
            item, self.items = self.items[0], self.items[1:]
        return item


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

if __name__ == "__main__":
    store = ItemStore("test")
    def producer():
        tag = {
            'id': 'aa',
            'count': 3
        }
        store.add_splitted(tag,"item 1/3")
        time.sleep(1)
        store.add_splitted(tag,"item 2/3")
        time.sleep(1)
        store.add_splitted(tag,"item 3/3")




    print('hhhh')
