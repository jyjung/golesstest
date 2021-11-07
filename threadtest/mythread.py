# thread 의 ident 값을 이용해서 처리하는지 context 라던지 기타 정보를 가져올수 있게 하자.  

import threading


def worker():
    print(threading.current_thread().name)
    print(threading.get_ident())


threading.Thread(target=worker).start()
threading.Thread(target=worker, name='foo').start()