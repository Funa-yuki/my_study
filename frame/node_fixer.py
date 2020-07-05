from inserted_functions import *

import ast
import re

class NodeFixer(object):
    def __init__(self):
        self.node_fix_functions = []

    def add(self, fixed_func):
        def wrapper(decorated_function):
            self.node_fix_functions.append(decorated_function)
        return wrapper(fixed_func)

    def fixNodes(self, nodes):
        for fix_func in self.node_fix_functions:
            nodes = fix_func(nodes)
        return nodes

node_fixer = NodeFixer()

### framework fixers ###
@node_fixer.add
def insert_query_checker(ast_callbacks):
    new_ast_callbacks = []
    for ast_callback in ast_callbacks:
        node = ast_callback.get('ast')
        new_node = InsertQueryChecker().visit(node)
        new_ast_callbacks.append({
            'callback_name': ast_callback.get('callback_name'),
            'method': ast_callback.get('method'),
            'path': ast_callback.get('path'),
            'path_compiled': ast_callback.get('path_compiled'),
            'ast': new_node
        })
    return new_ast_callbacks

# test code print -> reverse_print
@node_fixer.add
def rewrite_print_to_reverse_print(ast_callbacks):
    new_ast_callbacks = []
    for ast_callback in ast_callbacks:
        node = ast_callback.get('ast')
        new_node = RewriteReversePrint().visit(node)
        new_ast_callbacks.append({
            'callback_name': ast_callback.get('callback_name'),
            'method': ast_callback.get('method'),
            'path': ast_callback.get('path'),
            'path_compiled': ast_callback.get('path_compiled'),
            'ast': new_node
        })
    return new_ast_callbacks

# 権限をチェックして、権限がないやつに自動で追加するやつ
@node_fixer.add
def check_and_insert_is_admin(ast_callbacks):
    # Node: If(test=Call(func=Name(id='auth', ctx=Load()), args=[Name(id='request', ctx=Load())], keywords=[]), body=[Return(value=Str(s='Admin'))], orelse=[Return(value=Str(s='LOGIN'))])
    # から ifでauth() -> return "Admin"の情報を得る必要がある

    '''
    return_nodes_from_is_adminに
    if is_admin(request):
        return 'hoge'
    を満たすast.Returnオブジェクトを探してリストに格納
    '''
    return_nodes_from_is_admin = []
    for ast_callback in ast_callbacks:
        node = ast_callback.get('ast')
        ret_node = search_return_node_from_if_auth_func(node=node, auth_func_name='is_admin')
        if ret_node:
            if len(return_nodes_from_is_admin) is 0:
                return_nodes_from_is_admin.append(ret_node)
            else:
                for n in return_nodes_from_is_admin:
                    if ast.dump(n) is not ast.dump(ret_node):
                        continue
                    else:
                        return_nodes_from_is_admin.append(ret_node)
                        break
    #return_nodes_from_is_adminの要素と同じもののうち、if is_adminに入っていないものを探す
    for ast_callback in ast_callbacks:
        pass
    return ast_callbacks

### ast Transformer Subclasses
class InsertQueryChecker(ast.NodeTransformer):
    def visit_Call(self, node):
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                if node.func.value.id is 'cur':
                    if node.func.attr is 'execute':
                        new_args = []
                        for arg in node.args:
                            new_arg = ast.Call(
                                func=(ast.Name(id='escape_special_query', ctx=ast.Load())),
                                args=[arg],
                                keywords=[]
                            )
                            new_args.append(new_arg)
                        new_node = ast.Call(
                            func=node.func,
                            args=new_args,
                            keywords=node.keywords
                        )
                        return ast.copy_location(new_node, node)
        return node

class RewriteReversePrint(ast.NodeTransformer):
    def visit_Name(self, node):
        if node.id is 'print':
            new_node = ast.Name(
                id='reverse_print',
                ctx=ast.Load()
            )
            return ast.copy_location(new_node, node)
        return node


### search functions ###
def search_return_node_from_if_auth_func(node, auth_func_name):
    for n in ast.walk(node):
        if isinstance(n, ast.If):
            print(ast.dump(n))
            if isinstance(n.test, ast.Call) and n.test.func.id is auth_func_name:
                for body in n.body:
                    for b in ast.walk(body):
                        if isinstance(b, ast.Return):
                            return b
    return None

### test code
if __name__=="__main__":
    import inspect
    for f in node_fixer.node_fix_functions:
        print(inspect.getsource(f))
