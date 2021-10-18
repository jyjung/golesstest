#  item을 나눠서 저장하고.  다 저장되었으면 값을 리턴
import threading 

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

if __name__ == '__main__':
    test = {
        "id1":[1,2,3,4,5,6],
        "id7":[1,2,3,4]
    }
    aaa = test.pop('id1',None)
    print(test)
    print(aaa)