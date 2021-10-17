#async 기능을 이용해서 대기기간이 필요한 파이프 작업 처리.  
#signal 의 신호를 제대로 받아서 처리하는지 확인.  

import asyncio
import uuid
import time
from datetime import datetime
import gevent
from threading import Thread
from queue import Queue
from expiringdict import ExpiringDict

cache_dict = ExpiringDict(max_len=1000, max_age_seconds=10)


async def fake_file_download()-> str:
    id = str(uuid.uuid4()) + ".docx"
    await asyncio.sleep(0.4)
    return id

async def fake_file_upload(filename: str):
    await asyncio.sleep(0.5)
    return 
    

def fake_file_encoding_start()-> str:
    id = str(uuid.uuid4())
    cache_dict[id] = time.time()
    return id

def fake_file_encoding_status( id: str)-> bool:
    if id in cache_dict  and  time.time() - cache_dict[id] > 2:
        return True
    else:
        return False

async def wait_until_complete(filename: str):
    id = fake_file_encoding_start()
    for i in range(20):
        if fake_file_encoding_status(id):
            return True
        await asyncio.sleep(0.5)
    return False

async def step1_filedownload(in_queue:asyncio.Queue, out_queue:asyncio.Queue):
    while True:
        filename = await in_queue.get()
        print('step1',filename)
        temp_file_name = await fake_file_download()
        in_queue.task_done()
        print('before outque',filename)
        await out_queue.put(temp_file_name)


async def step2_file_encoding(in_queue:asyncio.Queue , out_queue:asyncio.Queue):
    while True:
        filename = await in_queue.get()
        print('step2',filename)        
        # process the token received from a producer
        work_result = await wait_until_complete(filename)
        in_queue.task_done()
        if work_result:
            await out_queue.put(filename)
 
async def step3_fileupload(in_queue:asyncio.Queue ):
    while True:
        filename = await in_queue.get()
        print('step3',filename)
        await fake_file_upload()
        in_queue.task_done()
 
 
async def pipe(fd_in_queue: asyncio.Queue):
    fd_out_ec_in_queue = asyncio.Queue()
    ec_out_fu_in_queue = asyncio.Queue()
    # fire up the both producers and consumers
    step1_functions = [asyncio.create_task(step1_filedownload(fd_in_queue,fd_out_ec_in_queue))
                 for _ in range(2)]
    step2_functions = [asyncio.create_task(step2_file_encoding(fd_out_ec_in_queue,ec_out_fu_in_queue))
                 for _ in range(5)]
    step3_functions = [asyncio.create_task(step3_fileupload(ec_out_fu_in_queue))
                 for _ in range(2)]
    print('step3 funcitons task end')
    await asyncio.gather(*step1_functions)
    print('end pipe')
    
def pipewrap(queue: Queue):
    fd_in = asyncio.Queue()
    t =Thread(target=asyncio.run, args=(pipe(fd_in),))
    t.daemon = False
    t.start()
    while True:
        filename = queue.get()
        print('get file',filename)
        asyncio.run(fd_in.put(filename))
        


def main():
    start = time.time()
    tlist =[]
    fd_in = Queue()
    for i in range(1):
        t =Thread(target=pipewrap, args=(fd_in,))
        t.daemon = False
        t.start()
        tlist.append(t)

    fd_in.put('first_file')
    time.sleep(5)        
    fd_in.put('second_file')
    
    for t in tlist:
        t.join()
    print(time.time()-start)

async def main2():
    start = time.time()
    tlist =[]
    fd_in = asyncio.Queue()
    await fd_in.put('first file')
    await fd_in.put('second file')
    await pipe(fd_in)

    print(time.time()-start)


if __name__ == '__main__':
    #asyncio.run(main2())
    main()
    


