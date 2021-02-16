from inserted_functions import *

import ast

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
def insert_query_checker(ast_callbacks):
    new_ast_callbacks = []
    for ast_callback in ast_callbacks:
        node = ast_callback.get('ast')
        new_node = InsertQueryChecker().visit(node)
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
    return_nodes_from_is_admin = []
    if_auth_ret_node_list = []
    new_callbacks = []
    dump_searched_ret_nodes = []

    # astのcallbackから if is_admin():下のreturnオブジェクトとelse:下のreturnオブジェクトを
    # [{'ret_node': ret_node, 'orelse_ret_node': orelse_ret_node}, {...}, ...]
    # の形でreturn_nodes_from_is_adminに格納するforループ
    for ast_callback in ast_callbacks:
        callback_node = ast_callback['ast']
        ret_node, orelse_ret_node = search_return_node_from_if_auth_func(node=callback_node, auth_func_name='is_admin')
        if ret_node:
            if_auth_ret_node_list.append(ret_node)
            return_nodes_from_is_admin.append({'ret_node':ret_node, 'orelse_ret_node':orelse_ret_node})

    # return_nodes_from_is_admin['ret_node']とdump内容が同じかつreturn_nodes_from_is_adminに入っていないreturnを探す
    for ast_callback in ast_callbacks:
        callback_node = ast_callback['ast']
        dump_searched_ret_nodes += search_same_dump_return_nodes(callback_node, if_auth_ret_node_list)

    # dumped_searched_ret_nodesの中でif_auth_ret_node_listに入っていないものを取り出す
    not_if_auth_ret_nodes = list(set(dump_searched_ret_nodes) - set(if_auth_ret_node_list))

    #コールバック関数の修正
    for ast_callback in ast_callbacks:
        callback_node = ast_callback["ast"]
        if not_if_auth_ret_nodes:
            for not_if_auth_ret_node in not_if_auth_ret_nodes:
                orelse_ret_node = search_orelse_node(return_nodes_from_is_admin, not_if_auth_ret_node)
                new_node = InsertIsAdminFunc(not_if_auth_ret_nodes, orelse_ret_node).visit(callback_node)
                new_callbacks.append(make_new_callback(ast_callback, new_node=new_node))
        else:
            new_callbacks.append(ast_callback)
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
        # argsとkeywordsを変更、escape_xss_characters()関数を噛ませる
        new_args = []
        new_keywords = []
        # return "...".format()を決める
        if isinstance(node.value, ast.Call):
            if isinstance(node.value.func, ast.Attribute):
                if node.value.func.attr == 'format':
                    for arg in node.value.args:
                        new_arg = ast.Call(
                            func=(ast.Name(id='escape_xss_characters', ctx=ast.Load())),
                            args=[arg],
                            keywords=[]
                        )
                        new_args.append(new_arg)

                    for keyword in keywords:
                        new_keyword = ast.Call(

                        )
                        new_keywords.append(new_keyword)

                    #後で消すところ
                    new_keywords = node.value.keywords
                    new_node = ast.Return(
                        value=ast.Call(
                            func=node.value.func,
                            args=new_args,
                            keywords=new_keywords
                        )
                    )
                    return ast.copy_location(new_node, node)
        return node

class InsertIsAdminFunc(ast.NodeTransformer):
    def __init__(self, ret_nodes, orelse_ret_node=None):
        self.ret_nodes = ret_nodes
        self.orelse_ret_node = orelse_ret_node

    def visit_Return(self, node):
        if node in self.ret_nodes:
            new_node = ast.If(
                test=ast.Call(
                    func=ast.Name(id='is_admin', ctx=ast.Load()),
                    args=[ast.Name(id='request', ctx=ast.Load())],
                    keywords=[]
                ),
                body=[node],
                #orelseを新しく作る必要がある
                orelse=[self.orelse_ret_node]
            )
            return ast.copy_location(new_node, node)
        return node

### search functions ###
def search_return_node_from_if_auth_func(node, auth_func_name):
    ret_node = None
    orelse_ret_node = None
    for n in ast.walk(node):
        if isinstance(n, ast.If):
            if isinstance(n.test, ast.Call) and isinstance(n.test.func, ast.Name) and n.test.func.id is auth_func_name:
                ret_node = search_ret_node(n.body)
                orelse_ret_node = search_ret_node(n.orelse)
    return ret_node, orelse_ret_node

def search_same_dump_return_nodes(node, ret_nodes):
    l = []
    for n in ast.walk(node):
        if isinstance(n, ast.Return):
            for ret_node in ret_nodes:
                if ast.dump(n) == ast.dump(ret_node):
                    l.append(n)
    return l

def search_ret_node(nodes):
    for node in nodes:
        for n in ast.walk(node):
            if isinstance(n, ast.Return):
                return n
    return None

def search_orelse_node(nodes, not_if_auth_ret_node):
    for node_dict in nodes:
        if ast.dump(node_dict['ret_node']) == ast.dump(not_if_auth_ret_node):
            return node_dict['orelse_ret_node']
    return None

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
