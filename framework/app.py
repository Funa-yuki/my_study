#!/usr/bin/env python3

from router import *
import inspect
import re
import ast
from request import Request
from response import Response
from func_fixer import FuncFixer
from check import Check
from users import *
from wsgiref.simple_server import make_server
from wsgiref.headers import Headers
from bottle import jinja2_template as template

response = Response()

class App:
    def __init__(self):
        self.router = Router()
        self.check = Check()
        self.funcFixer = FuncFixer()
        # self.response = Response()

    def route(self, path=None, method='GET', callback=None):
        def decorator(callback_func):
            print("route_test: ", callback_func)
            self.router.add(method, path, callback_func)
            return callback_func
        return decorator(callback) if callback else decorator

    def addCheck(self, check):
        def checkDecorator(checkFunc):
            self.check.addFunc(checkFunc)
            return checkFunc
        return checkDecorator(check) if check else checkDecorator

    '''
    def addCallbacks(self, callback):
        # callbackのreturnに関数名とローカル変数を戻り値に追加
        callback_txt = inspect.getsource(callback)
        lineno = 0
        callback_add_locals = ""
        ret_patturn = re.compile('\s*return\s+?')
        for line in callback_txt.splitlines():
            if re.match(ret_patturn, line):
                indent = re.match("^\s*", line).group()
                line = indent + re.sub(ret_patturn, "return inspect.currentframe().f_code.co_name, locals(), ", line)
            callback_add_locals = callback_add_locals + line + "\n"
        callback_add_locals = callback_add_locals + '\nself.new_callback = {}\n'.format(callback.__name__)
        exec(callback_add_locals)
        return self.new_callback
    '''

    def __call__(self, env, start_response):
        request = Request(env)
        # ユーザごとの動きの検出とそのためのインスタンスの探索, 作成
        ip_addr = request.client_ip_addr
        callback, status, kwargs = self.router.match(request.method, request.path)
        '''
        if status == '200':
            print("test1")
            new_callback = self.addCallbacks(callback)
            func_name, locals, body = new_callback(request, **kwargs)
            self.check(ip_addr, func_name, locals)
        '''
        if callback:
            body = callback(request, **kwargs)
        else:
            body = '404 Not Found'

        response.addBody(body)
        response.makeStatusCode(status)
        #responseのためのあれ
        status_code, headers, encoded_body = response.makeResponse()
        # set_cookie?
        start_response(status_code, headers)
        return encoded_body

# test_code
app = App()

class RewritePrintToReversePrint(ast.NodeTransformer):
    def visit_Name(self, node):
        if node.id is 'print':
            new_node = ast.Name(
                id='reversePrint',
                ctx=ast.Load()
            )
            return ast.copy_location(new_node, node)
        return node

class RewriteStringHogeToFuga(ast.NodeTransformer):
    def visit_Str(self, node):
        if node.s == 'hoge':
            new_node = ast.Str(s='fuga')
            return ast.copy_location(new_node, node)
        return node

@app.funcFixer.addNodeFixer
def hogeToFuga(node):
    new_node = RewriteStringHogeToFuga().visit(node)
    return new_node

@app.route("^/$", "GET")
@app.funcFixer.fix("hogeToFuga")
def index(request):
    print("hoge")
    return "hoge"


if __name__=="__main__":
    with make_server('', 8000, app) as httpd:
        print('Serving HTTP on port 8000')
        httpd.serve_forever()
