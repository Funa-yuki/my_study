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
        new_ast_callbacks.append(make_new_callback(ast_callback, new_node=new_node))
    return new_ast_callbacks

# test code print -> reverse_print
@node_fixer.add
def rewrite_print_to_reverse_print(ast_callbacks):
    new_ast_callbacks = []
    for ast_callback in ast_callbacks:
        node = ast_callback.get('ast')
        new_node = RewriteReversePrint().visit(node)
        new_ast_callbacks.append(make_new_callback(ast_callback, new_node=new_node))
    return new_ast_callbacks


@node_fixer.add
def rewrite_for_xss(ast_callbacks):
    new_ast_calbacks = []
    for ast_callback in ast_callbacks:
        node = ast_callback.get('ast')
        new_node = SanitizeReturnValueUsingFormat().visit(node)
    return ast_callbacks


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
    new_callbacks = []
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
        node = ast_callback.get("ast")
        ret_nodes = has_return_nodes(node, return_nodes_from_is_admin)
        if not ret_nodes:
            new_callbacks.append(ast_callback)
        else:
            new_node = None
            for ret_node in ret_nodes:
                print(ast.dump(node))
                if not from_is_admin(node, ret_node):
                    #if is_adminノードの追加
                    new_node = InsertIsAdminFunc(ret_node).visit(node)
            new_callbacks.append(make_new_callback(ast_callback, new_node=new_node))
    return new_callbacks

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

class SanitizeReturnValueUsingFormat(ast.NodeTransformer):
    def visit_Return(self, node):
        new_args = []
        new_keywords = []
        new_value = []
        if isinstance(node.value, ast.Call):
            if isinstance(node.value.func, ast.Attribute):
                if node.value.func.attr == 'format':
                    print(ast.dump(node))
                    for arg in node.value.args:
                        new_arg = ast.Call(
                            func='escape_xss_characters',
                            args=[arg],
                            ctx=ast.Load(),
                        )
                        new_args.append(new_arg)
                    for keyword in node.value.keywords:
                        #keyword の引数にcall(escape_xss_charactersを上書き)
                        new_keyword = ast.keyword(
                            arg = keyword.arg,
                            value = keyword.value,
                        )
                        new_keywords.append(new_keyword)
                    if new_args:
                        print(new_args)
                    print()

                    if new_keywords:
                        print(new_keywords)
                    print()
                    new_node = node
                    return ast.copy_location(new_node, node)
        return node


class InsertIsAdminFunc(ast.NodeTransformer):
    def __init__(self, ret_node):
        self.ret_node = ret_node

    def visit_Return(self, node):
        # condition は is_admin
        # 本当はorelse=[ast.Return(loginページ)]にする必要がある
        if ast.dump(self.ret_node) == ast.dump(node):
            new_node = ast.If(
                test=ast.Call(
                    func=ast.Name(id='is_admin', ctx=ast.Load()),
                    args=[ast.Name(id='request', ctx=ast.Load())],
                    keywords=[]
                ),
                body=[node],
                orelse=[ast.Return(value=ast.Str(s='LOGIN'))]
            )
            return ast.copy_location(new_node, node)
        return node


### search functions ###
def search_return_node_from_if_auth_func(node, auth_func_name):
    for n in ast.walk(node):
        if isinstance(n, ast.If):
            if isinstance(n.test, ast.Call) and n.test.func.id is auth_func_name:
                for body in n.body:
                    for b in ast.walk(body):
                        if isinstance(b, ast.Return):
                            return b
    return None

# 一致するノードを探して、リストを返す
def has_return_nodes(node, return_nodes):
    l = []
    for n in ast.walk(node):
        if isinstance(n, ast.Return):
            for ret_node in return_nodes:
                if ast.dump(ret_node) == ast.dump(n):
                    l.append(n)
    return l

 # ifの条件がis_admin()から、ret_nodeに行くようなノードがあるか
def from_is_admin(node, ret_node):
    for n in ast.walk(node):
        if isinstance(n, ast.If) and have_is_admin_condition(n):
            if search_ret_node(node, ret_node):
                return True
    return False

# nodeはast.Ifでそれがis_admin()を条件にしているか
def have_is_admin_condition(node):
    condition = node.test
    if isinstance(condition, ast.Call):
        for n in ast.walk(condition):
            if isinstance(n, ast.Name) and n.id == 'is_admin':
                return True
    return False


# nodeはast.If, ノード下にret_nodeが入っている場合True
def search_ret_node(node, ret_node):
    body = node.body
    for b in body:
        for node in ast.walk(b):
            if isinstance(node, ast.Return):
                if ast.dump(node) == ast.dump(ret_node):
                    print(ast.dump(node))
                    return True
    return False

def make_new_callback(callback, new_node=None):
    new_callback = {}
    if new_node:
        new_callback = {
            'callback_name': callback.get('callback_name'),
            'method': callback.get('method'),
            'path': callback.get('path'),
            'path_compiled': callback.get('path_compiled'),
            'ast': new_node
        }
        return new_callback
    return callback



### test code
if __name__=="__main__":
    import inspect
    for f in node_fixer.node_fix_functions:
        print(inspect.getsource(f))
