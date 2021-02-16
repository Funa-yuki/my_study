#!/usr/bin/env python3

from router import *
import inspect
import re
import ast
from request import Request
from response import Response
from func_fixer import FuncFixer
from FrameworkFixer import *
from check import Check
from users import *
from wsgiref.simple_server import make_server
from wsgiref.headers import Headers
import redis
import uuid

# 乱数: "admin" or "general"
user_roll_db = redis.Redis(host="localhost", port=6379, db=0)
response = Response()

class App:
    def __init__(self):
        self.router = Router()
        self.check = Check()
        self.funcFixer = FuncFixer()
        # self.response = Response()

    def route(self, path=None, method='GET', callback=None):
        def decorator(callback_func):
            #default_fixer
            self.router.add(method, path, callback_func)
            return callback_func
        return decorator(callback) if callback else decorator

    def addCheck(self, check):
        def checkDecorator(checkFunc):
            self.check.addFunc(checkFunc)
            return checkFunc
        return checkDecorator(check) if check else checkDecorator

    def setDefaultCookie(self, cookies):
        try:
            user_id = cookies["uid"].value
        except:
            user_id = None

        if user_id is None or not user_roll_db.get(user_id):
            rand = uuid.uuid4().hex
            while user_roll_db.get(rand) is not None:
                rand = uuid.uuid4().hex
            user_id = rand
            #redisの登録(expireを1時間にする)
            user_roll_db.set(user_id, "general")
            user_roll_db.expire(user_id, 3600)
            # responseのsetcookie
            response.setCookies(name="uid", value=user_id)

    def run(self, port=8000):
        #self.fixed_router = FixedRouter(self.router)
        #self.router = self.fixed_router
        with make_server('', port, app) as httpd:
            print('Serving HTTP on port {}'.format(port))
            httpd.serve_forever()

    def __call__(self, env, start_response):
        request = Request(env)
        # ユーザごとの動きの検出とそのためのインスタンスの探索, 作成
        ip_addr = request.client_ip_addr
        callback, status, kwargs = self.router.match(request.method, request.path)
        self.setDefaultCookie(request.cookies)
        if callback:
            body = callback(request, **kwargs)
        else:
            body = '404 Not Found'

        response.addBody(body)
        response.makeStatusCode(status)
        #responseのためのあれ
        status_code, headers, encoded_body = response.makeResponse()
        start_response(status_code, headers)
        return encoded_body


##### コールバック関数内部で利用されるヘルパーたち ####
def check_auth(request, id=None, password=None, dbname=None):

    try:
        default_cookie = request.cookies["uid"].value
    except:
        default_cookie = ""
    if default_cookie:
        # redis
        roll = user_roll_db.get(default_cookie)
        print(roll)
        if roll == b'admin':
            return True
        else:
            if has_admin_account(id=id, password=password, dbname=dbname):
                #set "admin" for user_roll
                user_roll_db.set(default_cookie, "admin")
                user_roll_db.expire(default_cookie, 3600)
                return True
    #print("general")
    return False

# インスタンスにして from app import app　から実行できるようにしてる
app = App()



# test_code
if __name__=="__main__":
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

        def visit_Name(self, node):
            if node.id is 'print':
                new_node = ast.Name(
                    id='reversePrint',
                    ctx=ast.Load()
                )
                return ast.copy_location(new_node, node)
            return node
    @app.funcFixer.addNodeFixer
    def rewriteNode(node):
        new_node = RewriteStringHogeToFuga().visit(node)
        return new_node

    @app.route("^/hoge$", "GET")
    @app.funcFixer.fix("rewriteNode")
    def index(request):
        print("hoge")
        return "Hello"

    with make_server('', 8000, app) as httpd:
        print('Serving HTTP on port 8000')
        httpd.serve_forever()
