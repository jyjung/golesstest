"""
This file demonstrates the pipeline pattern.
A pipeline is used where a series of steps (goroutines) process
data in serial.

The example calculates the md5 checksums
for all files in the current directory.
It is split into a stage that reads the file in the folder,
a stage that calculates the md5 using several goroutines,
and a stage that collects the results.

See http://blog.golang.org/pipelines for more info.
"""

from __future__ import print_function
import time
from threading import Thread
import hashlib
import os
import uuid 
import time
from typing import Tuple,Dict,Any,Callable

import goless
import time
import gevent


gdict = {}

def fake_begin_mip()-> str:
    id = str(uuid.uuid4())
    gdict[id] = time.time()
    return id

def fake_status( id: str)-> bool:
    if id in gdict  and  time.time() - gdict[id] > 2:
        return True
    else:
        return False

def test1():
    id = fake_begin_mip()
    print(id)
    print(gdict[id])
    for i in range(5):
        print(fake_status(id))
        time.sleep(1)






def make_gen(sleep_time: float):
    def _inner():
        nonlocal sleep_time
        names = ["jung","kim","hong","bae","park"]
        for i in names:
            gevent.sleep(sleep_time)
            yield i
            
    return _inner

#print(next(gen2()))
def pipeline(index):
    gen1 = make_gen(0.5)
    gen2 = make_gen(0.5)
    gen3 = make_gen(1)

    files = goless.chan(1)
    hashes = goless.chan(1)
    results = goless.chan(1)

    def file_works():
        for i in gen1():
            files.send(i)
        files.close()

    def simul_mip_api():
        for f in files:
            g= next(gen2())
            n = f + "---" + g
            hashes.send(n)
        hashes.close()

    def collector():
        for f in  hashes:
            g= next(gen3())
            n = f + "---" + g
            results.send(n)
            
        results.close()

    def collector2():
        for f in  hashes:
            g= next(gen3())
            n = f + "---" + g
            results.send(n)
            
        results.close()


    goless.go(file_works)
    goless.go(simul_mip_api)
    goless.go(collector)
    goless.go(collector2)    

    for f in results:
        print('[%d] %s' % (index, f))

def main1():
    start = time.time()
    tlist =[]
    for i in range(1000):
        t =Thread(target=pipeline, args=(i,))
        t.daemon = False
        t.start()
        tlist.append(t)
    for t in tlist:
        t.join()
    print(time.time()-start)


if __name__ == '__main__':
    main1()


