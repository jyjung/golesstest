import threading

class WorkingItem:
    def __init__(self,filename: str, id:str):
        self.filename = filename
        self.id = id
    def __str__(self) -> str:
        return "file[{file}]:id[{id}]".format(file=self.filename,id=self.id)


class ItemStore(object):
    def __init__(self):
        self.cond = threading.Condition()
        self.items = []

    def add(self, item):
        with self.cond:
            self.items.append(item)
            self.cond.notify() # Wake 1 thread waiting on cond (if any)

    def get_all(self, blocking=False):
        with self.cond:
            # If blocking is true, always return at least 1 item
            while blocking and len(self.items) == 0:
                self.cond.wait()
            items, self.items = self.items, []
        return items

if __name__ == '__main__':
    a =WorkingItem('fff','bbb')
    print(a.filename)
