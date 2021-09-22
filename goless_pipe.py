#async 기능을 이용해서 대기기간이 필요한 파이프 작업 처리.  
#signal 의 신호를 제대로 받아서 처리하는지 확인.  

import asyncio
import threading
import uuid
import time
from datetime import datetime
import gevent
import goless
from threading import Thread
from queue import Queue
from typing import Union
from expiringdict import ExpiringDict

cache_dict = ExpiringDict(max_len=1000, max_age_seconds=10)

def fake_file_download()-> str:
    id = str(uuid.uuid4()) + ".docx"
    gevent.sleep(0.4)
    return id

def fake_file_upload(filename: str):
    gevent.sleep(0.5)

def fake_file_encoding_start(filename: str)-> str:
    id = str(uuid.uuid4())
    cache_dict[id] = time.time()
    return id

def fake_file_encoding_status( id: str)-> bool:
    if id in cache_dict  and  time.time() - cache_dict[id] > 2:
        return True
    else:
        return False

def wait_until_complete(filename: str):
    id = fake_file_encoding_start(filename)
    for i in range(20):
        print('wait_until_complete',i)
        if fake_file_encoding_status(id):
            print('wait True')
            return True
        gevent.sleep(0.5)
        #time.sleep(0.5)
        
    return False


 
def pipe(queue:Queue):
    #step1 = goless.chan()
    step2 = goless.chan(-1)
    step3 = goless.chan(-1)
    results = goless.chan(-1)    

    def step1_filedownload( ):
        print('step1 begin')
        #for item in step1:
        while True:
            item = queue.get()
            print('step1',item)
            temp_file_name = fake_file_download()
            mydict= {
                "traceid": item,
                "value": temp_file_name
            }
            print('step1 before send ')
            step2.send(mydict)
            print('step1 send complete')
        print('step1 end')

    def step2_file_encoding():
        print('step2 begin')        
        for item2 in step2: 
            print('step2',item2['traceid'],item2['value'])        
            work_result = wait_until_complete(item2['value'])
            if work_result:
                mydict2= {
                    "traceid": item2['traceid'],
                    "value": item2['value']
                }
                print('step2 before send ')
                step3.send(mydict2)
                print('step3 send complete')
        print('step2 end')
            
    def step3_fileupload():
        print('step3 begin')
        for item3 in step3:
            print('step3',item3['traceid'],item3['value'])        
            fake_file_upload(item3['value'])
            results.send(item3)
        print('step3 end')    
        
    goless.go(step1_filedownload)
    goless.go(step2_file_encoding)
    goless.go(step3_fileupload)

    for item in results:
        print('out result',item)

def pipe2(filelist):
    #step1 = goless.chan()
    step2 = goless.chan()
    step3 = goless.chan()
    results = goless.chan()    

    def step1_filedownload( ):
        print('step1 begin')
        #for item in step1:
        
        for item in filelist:
            print('step1',item)
            temp_file_name = fake_file_download()
            mydict= {
                "traceid": item,
                "value": temp_file_name
            }
            print('step1 before send ')
            step2.send(mydict)
            print('step1 send complete')
        print('step1 end')
        step2.close()



    def _inner_until_complete(filename: str):
        id = fake_file_encoding_start(filename)
        for i in range(20):
            print('wait_until_complete',i)
            if fake_file_encoding_status(id):
                print('wait True')
                return True
            gevent.sleep(0.5)
        return False




    def step2_file_encoding():
        print('step2 begin')        
        for item2 in step2: 
            print('step2',item2['traceid'],item2['value'])        
            work_result = wait_until_complete(item2['value'])
            if work_result:
                mydict2= {
                    "traceid": item2['traceid'],
                    "value": item2['value']
                }
                print('step2 before send ')
                step3.send(mydict2)
                print('step3 send complete')
        step3.close()
        print('step2 end')
            
    def step3_fileupload():
        print('step3 begin')
        for item3 in step3:
            print('step3',item3['traceid'],item3['value'])        
            fake_file_upload(item3['value'])
            results.send(item3)
        results.close()
        print('step3 end')    
        
    goless.go(step1_filedownload)
    goless.go(step2_file_encoding)
    goless.go(step3_fileupload)
    

    for item in results:
        print('out result',item)
    print('end')

   

def main():
    start = time.time()
    tlist =[]
    fd_in = Queue()

    for i in range(3):
        t =Thread(target=pipe, args=(fd_in,))
        t.daemon = False
        t.start()
        tlist.append(t)

    fd_in.put('first1_file')
    gevent.sleep(4)        
    fd_in.put('first2_file')    
    gevent.sleep(4)        
    fd_in.put('first3_file')        
    # gevent.sleep(2)        
    # fd_in.put('second_file')
    # gevent.sleep(2)        
    # fd_in.put('third_file')
    # gevent.sleep(2)        
    # fd_in.put('fourth_file')
    while True:
        time.sleep(1)
    
    for t in tlist:
        t.join()
    print(time.time()-start)

def main2():
    start = time.time()
    filelist = ['first_file','second_file','third_file']
    pipe2(filelist)
    print(time.time()-start)
    
if __name__ == '__main__':
    main2()
    


