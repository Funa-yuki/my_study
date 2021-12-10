from node_fixer import node_fixer
from inserted_functions import *

import ast
import inspect
import copy

#server.pyのimportをここに適用させてあげる必要がある？
#from bottle import jinja2_template as tmpl
#import sqlite3

class Fix(object):
    def __init__(self):
        self.fixed_routes = []
        self.node_fixer = node_fixer

    def fix(self, routes):
        asts = self.codeToASTs(routes)
        fixed_asts = node_fixer.fixNodes(asts)
        fixed_routes = []
        # for exec
        for fixed_ast in fixed_asts:
            node = fixed_ast.get('ast')
            callback_name = fixed_ast.get('callback_name')
            exec(compile(ast.fix_missing_locations(node), filename="<ast>", mode="exec"))
            fixed_callback = locals().get(callback_name)
            fixed_route = ({
                'method':fixed_ast.get('method'),
                'path': fixed_ast.get('path'),
                'path_compiled': fixed_ast.get('path_compiled'),
                'callback': fixed_callback
            })
            fixed_routes.append(fixed_route)
        return fixed_routes

    def codeToASTs(self, routes):
        asts = []
        for route in routes:
            callback_name = route.get('callback').__name__
            source = inspect.getsource(route.get('callback'))
            source = self.fixIndent(source)
            source = self.removeRouteDecorator(source)
            node = ast.parse(source)
            asts.append({
                'callback_name': callback_name,
                'method': route.get('method'),
                'path': route.get('path'),
                'path_compiled': route.get('path_compiled'),
                'ast': node
            })
        return asts

    def fixIndent(self, source):
        indent = 0
        fixed_source = ''
        lines = source.splitlines()
        for num in range(len(lines)):
            if num is 0 and lines[0][0] is ' ':
                for character in lines[0]:
                    if character is ' ':
                        indent += 1
                    else:
                        break
            fixed_source += lines[num].replace(' '*indent, '', 1)
            fixed_source += '\n'
        return fixed_source

    def removeRouteDecorator(self,source):
        lines = source.splitlines()
        fixed_source = ""
        for index in range(len(lines)):
            if lines[index].startswith("@"):
                break
        if len(lines) == index + 1:
            return source

        for i in range(index+1, len(lines)):
            fixed_source += lines[i] + "\n"
        return fixed_source


#test code
if __name__=="__main__":
    def index(request):
        print(request)
        return "INDEX"
    callback = index
    routes = [{
        'method': 'GET',
        'path': '/',
        'path_compiled': '/',
        'callback': callback
    }]
    fixer = Fix()
    fixered = fixer.fix(routes)
    print(fixered)
    fixered[0].get('callback')("hoge")
