#async 기능을 이용해서 대기기간이 필요한 파이프 작업 처리.  

import asyncio
import uuid
import time
from datetime import datetime
import gevent

gdict = {}

async def fake_begin_mip()-> str:
    id = str(uuid.uuid4())
    gdict[id] = time.time()
    return id

async def fake_status( id: str)-> bool:
    if id in gdict  and  time.time() - gdict[id] > 2:
        return True
    else:
        return False

async def sync_test_work():
    id = await fake_begin_mip()
    for i in range(5):
        print(datetime.now(), id, await fake_status(id))
        #gevent.sleep(1)
        #time.sleep(1)
        await asyncio.sleep(1)

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

