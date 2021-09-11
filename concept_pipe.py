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

import goless
import time
import gevent



def make_gen():
    def _inner():
        names = ["jung","kim","hong","bae","park"]
        for i in names:
            gevent.sleep(1)
            yield i
            
    return _inner

#print(next(gen2()))
def pipeline(index):
    gen1 = make_gen()
    gen2 = make_gen()
    gen3 = make_gen()

    files = goless.chan(5)
    hashes = goless.chan(5)
    results = goless.chan(5)

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

    goless.go(file_works)
    goless.go(simul_mip_api)
    goless.go(collector)

    for f in results:
        print('[%d] %s' % (index, f))


if __name__ == '__main__':
    start = time.time()
    #pipeline(1)

    tlist =[]
    for i in range(5):
        t =Thread(target=pipeline, args=(i,))
        t.daemon = False
        t.start()
        tlist.append(t)
    for t in tlist:
        t.join()
    print(time.time()-start)


