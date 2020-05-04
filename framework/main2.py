#!/usr/bin/env python3

from app import *
from bottle import jinja2_template as template
from app import response
from check import *
from wsgiref.simple_server import make_server

import inspect
import ast

@app.addFixer
def customFixer1(callback): #callback_tree : <ast.Module>
    def reversePrint(s):
        print(s[:-1])

    class RewriteReverse(ast.NodeTransformer):
        def visit_Name(node):
            if node.id is "print":
                new_node = ast.Name(
                    id='reversePrint',
                    ctx=ast.Load()
                )
                return ast.copy_location(new_node, node)
            return node

    callback_tree = CallbackAstGenerator(callback)
    new_callback_tree = RewriteReverse().visit(callback_tree)
    exec(compile(ast.fix_missing_locations(new_callback_tree), filename="<ast>", mode="exec"))
    return new_callback_ast

def CallbackAstGenerator(callback):
    callback_txt = inspect.getsource(callback)
    callback_ast = ast.parse(callback_txt)
    return callback_ast

# @noSanitizeForSqlInjection
@app.route("^/$", "GET")
@cusutomFixer1
def index(request):
    print("hogehoge")
    return "Index Page"

if __name__=="__main__":
    port = 8080
    with make_server('', port, app) as httpd:
        print('Serving HTTP on port {}'.format(port))
        httpd.serve_forever()
