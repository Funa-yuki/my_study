#!/usr/bin/env python3

import re
from users import *

class Check:
    def __init__(self):
        self.users = Users()
        self.funcs = []

    def addFunc(self, func):
        self.funcs.append(func)

    def check(self, user):
        for checkfunc in self.funcs:
            checkfunc(user)

    def __call__(self, ip_addr, route_func_name, localargs):
         user = self.users.usersUpdate(ip_addr, route_func_name, localargs)
         self.check(user)
        #pass

def check1(user):
    a = 1
    b = 2
    print(user.locals.get('route1'))
    print()

def check2(user):
    print(user.locals.get('route2'))
    print()

def route1():
    a = 1
    b = 2
    c = '<script>alert(1)</script>'
    return locals()

def route2():
    a = 1
    b = 3
    return locals()

if __name__=="__main__":
    check = Check()
    check.addFunc(check1)
    check.addFunc(check2)

    localargs = route1()
    check('192.168.0.0', 'route1', localargs)
    localargs = route2()
    check('192.168.0.0', 'route2', localargs)
