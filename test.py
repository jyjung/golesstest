import copy 

def abc(**kwargs):
    for key,value  in kwargs.items():
        print(key,value)

if __name__ == '__main__':
    abc(tag='aaaa', nice='bbbbb')

