import copy 

def secret_hide(secret: str) -> str:
    if  len(secret) < 8 : 
        return '*' * len(secret)
    else:
        return secret[0:4] + "-" * (len(secret) - 7)  + secret[-3:]



if __name__ == '__main__':
    dd = {
        "aaa" : "1234",
        "secret": "secret_real_jung_jin_young"
    }

    cc = copy.copy(dd)
    cc['secret'] = secret_hide(dd['secret'])
    print(cc['secret'])
    print(dd['secret'])
    


