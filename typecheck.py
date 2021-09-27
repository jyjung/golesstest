from typing import Any
import functools

def type_check(func):
    @functools.wraps(func)
    def check(*args, **kwargs):
        for i in range(len(args)):
            v = args[i]
            v_name = list(func.__annotations__.keys())[i]
            v_type = list(func.__annotations__.values())[i]
            error_msg = 'Variable `' + str(v_name) + '` should be type ('
            error_msg += str(v_type) + ') but instead is type (' + str(type(v)) + ')'
            if not isinstance(v, v_type):
                raise TypeError(error_msg)

        result = func(*args, **kwargs)
        v = result
        v_name = 'return'
        v_type = func.__annotations__['return']
        error_msg = 'Variable `' + str(v_name) + '` should be type ('
        error_msg += str(v_type) + ') but instead is type (' + str(type(v)) + ')'
        if not isinstance(v, v_type):
                raise TypeError(error_msg)
        return result

    return check


def type_check2(func):
    @functools.wraps(func)
    def check(*args, **kwargs):
        for name, value in kwargs.items():
            v = value
            v_name = name
            if name not in func.__annotations__:
                continue
                
            v_type = func.__annotations__[name]

            error_msg = 'Variable `' + str(v_name) + '` should be type ('
            error_msg += str(v_type) + ') but instead is type (' + str(type(v)) + ') '
            if not isinstance(v, v_type):
                raise TypeError(error_msg)

        result = func(*args, **kwargs)
        if 'return' in func.__annotations__:
            v = result
            v_name = 'return'
            v_type = func.__annotations__['return']
            error_msg = 'Variable `' + str(v_name) + '` should be type ('
            error_msg += str(v_type) + ') but instead is type (' + str(type(v)) + ')'
            if not isinstance(v, v_type):
                    raise TypeError(error_msg)
        return result

    return check

def my_check(func):
    def check(*args, **kwargs):
        for i in range(len(args)):
            v = args[i]
            v_name = list(func.__annotations__.keys())[i]
            v_type = list(func.__annotations__.values())[i]
            error_msg = 'Variable `' + str(v_name) + '` should be type ('
            error_msg += str(v_type) + ') but instead is type (' + str(type(v)) + ')'
            if not isinstance(v, v_type):
                raise TypeError(error_msg)

        result = func(*args, **kwargs)
        v = result
        v_name = 'return'
        v_type = func.__annotations__['return']
        error_msg = 'Variable `' + str(v_name) + '` should be type ('
        error_msg += str(v_type) + ') but instead is type (' + str(type(v)) + ')'
        if not isinstance(v, v_type):
                raise TypeError(error_msg)
        return result
    return check


@type_check
def test(name : list) -> float:
    return 3.0

@type_check
def test2(name : str) -> str:
    return 3.0


def aaa():
    return 11, "aaa"
def bbb( a,b):
    print(a,b)

def xxx():
    return 1
def ccc(c):
    print(c)

# 타입 체크를 이용해서  인풋 타입과 아웃풋 타입을 알아낸다.  
if __name__ == '__main__':
    print(test.__name__)
    newfunc = my_check(test)
    print(newfunc([1,2,3,4]))
    item = aaa()
    bbb(*item)



