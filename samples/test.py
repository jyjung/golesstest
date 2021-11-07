import copy 

def abc(**kwargs):
    for key,value  in kwargs.items():
        print(key,value)

if __name__ == '__main__':
    #abc(tag='aaaa', nice='bbbbb')
    aa = 'filestrfwefwef.zip'
    dd = [ aa[:-4] + v for v in ["aaa","bbb","ccc"] ]
    print(dd)

