#async 기능을 이용해서 대기기간이 필요한 파이프 작업 처리.  
#signal 의 신호를 제대로 받아서 처리하는지 확인.  

import asyncio
import uuid
import time
from datetime import datetime
import gevent
from expiringdict import ExpiringDict

cache_dict = ExpiringDict(max_len=1000, max_age_seconds=10)


async def fake_file_download()-> str:
    id = str(uuid.uuid4()) + ".docx"
    await asyncio.sleep(0.4)
    return id

async def fake_file_upload(filename: str):
    await asyncio.sleep(0.5)
    return 
    

def fake_begin_mip()-> str:
    id = str(uuid.uuid4())
    cache_dict[id] = time.time()
    return id

def fake_mip_status( id: str)-> bool:
    if id in cache_dict  and  time.time() - cache_dict[id] > 2:
        return True
    else:
        return False


async def sync_test_work(filename: str):
    id = fake_begin_mip()
    for i in range(20):
        if fake_mip_status(id):
            return True
        await asyncio.sleep(0.5)
    return False

async def step1_filedownload(in_queue:asyncio.Queue, out_queue:asyncio.Queue):
    while True:
        filename = await in_queue.get()
        temp_file_name = await fake_file_download()
        in_queue.task_done()
        out_queue.put(temp_file_name)


async def step2_mip(in_queue:asyncio.Queue , out_queue:asyncio.Queue):
    while True:
        filename = await in_queue.get()
        # process the token received from a producer
        work_result = await sync_test_work(filename)
        in_queue.task_done()
        if work_result:
            out_queue.put(filename)
            print(f'consumed {filename}')
 
async def step3_fileupload(in_queue:asyncio.Queue ):
    while True:
        filename = await in_queue.get()
        temp_file_name = await fake_file_upload()
        in_queue.task_done()
 
 
async def main():
    queue = asyncio.Queue()
 
    # fire up the both producers and consumers
    producers = [asyncio.create_task(producer(queue))
                 for _ in range(3)]
    consumers = [asyncio.create_task(consumer(queue))
                 for _ in range(10)]


async def main():
    tasks = [
        sync_test_work(),
        sync_test_work(),
    ]

    while len(tasks):
        done, tasks = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        for task in done:
            print(task, task.result())


asyncio.run(main())

