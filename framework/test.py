#!/usr/bin/env python3

from app import *
from bottle import jinja2_template as template
from app import response
from check import *
from wsgiref.simple_server import make_server

app = App()
@app.route("^/$", "GET")
def hello(request):
    ip_addr = request.client_ip_addr
    response.setCookies(name='hogehogename', value='hooogggeee', max_age=30, httponly='yes')
    return template("./views/index.html")

@app.route("^/login$")
def login(request):
    name1=request.query
    return template("./views/login.html")

@app.route("^/doLogin$", "POST")
def doLogin(request):
    name = request.forms.get("name")
    password = request.forms.get("password")
    return "name: {} password: {}".format(name, password)

@app.route("^/index$", "GET")
def index(request):
    a = 3
    b = 2
    c = a - b
    if a == 3:
        a = 2
        return 'Other_Index'
    return 'Index'


'''
class User:
    def __init__(self, ip_addr):
        self.ip_addr = ip_addr
        self.locals = {}
    ...

user = User(ip_addr)
user.ip_addr: クライアントのip
user.locals: {@app.route下の関数名: 関数内のローカル関数, ...}
'''
@app.addCheck
def check(user):
    print(user.locals.get('doLogin'))



if __name__=="__main__":
    port = 8080
    with make_server('', port, app) as httpd:
        print('Serving HTTP on port {}'.format(port))
        httpd.serve_forever()
