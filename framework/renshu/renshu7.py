import ast

from renshu5 import findcursor

class Request:
    def __init__(self):
        self.params = {"ID": "2 or 2 = 2 order by ID desc;--", "Password":""}

class Rerequest:
    def __init__(self, request):
        self.params = self.nosqli_dict(request.params)

    def nosqli_dict(self, params):
        if isinstance(params, dict):
            d = {}
            for k, v in params.items():
                if k == "ID":
                    d[k] = "1"
                if k == "Password":
                    d[k] = "password"
        return d

source = '''
import sqlite3

def func1(request):
    conn = sqlite3.connect("test1.db")
    cur = conn.cursor()

    s1 = "select * from table1"
    s2 = " where ID = {}".format(request.params.get("ID"))
    s3 = " and Password = {}".format(request.params["Password"])
    s5 = " and Password = " + request.params["Password"]
    s4 = s1 + s2 + s5
    cur.execute(s4)
    #cur.execute("select * from table1 where ID = {} and Password = {}".format(request.params.get("ID"), request.params.get("Password")))
    #cur.execute("select * from table1 where ID = " + request.params.get("ID") + " and Password = " + request.params.get("Password"))
    data = cur.fetchone()
    conn.commit()
    return "Return: Hello, " + data[1] + ". Your ID is " + data[0]
'''

class RewriteNameToReRequest(ast.NodeTransformer):
    def visit_Name(self, node):
        if node.id == "request":
            new_node = ast.Name(id="rerequest", ctx=node.ctx)
            return new_node
        return node

def searchExecuteArgs(node, l):
    for a in ast.walk(node):
        if isinstance(a, ast.Call) and isinstance(a.func, ast.Attribute):
            if isinstance(a.func.value, ast.Name) and a.func.value.id in l:
                if a.func.attr == "execute":
                    #print(ast.dump(a))
                    for arg in a.args:
                        new_node = RewriteNameToReRequest().visit(arg)
                        new_node = ast.copy_location(new_node, node)
                        #print(ast.dump(node))
                    return node
    return node

# 代入した変数がrequestオブジェクトの何を利用しているか調べる
# {"s1": {attrs: [params["ID"], params["Password"]]}, s2: {attrs: [query["name"]]}}
class checkAssignRequest:
    def searchAssign(self, node, request_attr_list= ["path", "client_ip_addr", "method", "forms", "query", "params", "body"]):
        assign_dict = {}
        for a in ast.walk(node):
            if isinstance(a, ast.Assign):
                for i in range(len(a.targets)):
                    target = a.targets[i]
                    key = target.id
                    val = self.searchRequestAttribute(a, request_attr_list)
                    if val:
                        assign_dict[key] = val

        return assign_dict

    # d = {"attrs": {'params':['ID', 'Password'], 'text': None}}
    # request_attr_list = ["path", "client_ip_addr", "method", "forms", "query", "params", "body"]
    def searchRequestAttribute(self, node, request_attr_list):
        attr_request = self.searchRequest(node.value)
        if not attr_request:
            return None

        d = {}
        for n in ast.walk(node):
            if isinstance(n, ast.Attribute) and n.attr in request_attr_list:
                if n.attr == "forms" or n.attr == "params":
                    params = self.searchIndex(node)
                    attr = n.attr
                    d[attr] = params

                else:
                    pass
            elif isinstance(n, ast.Subscript):
                pass
        return d

    def searchRequest(self, node):
        for n in ast.walk(node):
            if isinstance(n, ast.Name) and n.id == 'request':
                return True
        return False

    def searchIndex(self, node):
        l = []
        for n in ast.walk(node):
            if isinstance(n, ast.Index):
                l.append(n.value.s)
            if isinstance(n, ast.Call):
                if isinstance(n.func, ast.Attribute) and n.func.attr is "get":
                    l.append(n.args[0].s)
        return l

class addAssign(object):
    # {..., 's4':{'params':['ID', 'Password']}}
    def addAssign(self, node, request_attr_dict):
        for n in ast.walk(node):
            if isinstance(n, ast.Assign):
                for target in n.targets:
                    if not target.id in request_attr_dict:
                        request_attr_dict = self.checkRequestVariable(n, target.id, request_attr_dict)
        return request_attr_dict

    # n.id : {'params': ["Password"], forms:["Name"], ... }
    def checkRequestVariable(self, node, id, d):
        key = id
        value = {}
        for n in ast.walk(node):
            if isinstance(n, ast.Name) and n.id in d:
                for k, v in d[n.id].items():
                    if k in value.keys():
                        if value[k] != v:
                            value[k] = value[k] + v
                            value[k] = list(set(value[k]))
                    else:
                        value[k] = v
        if value:
            d[id] = value
        return d

class FixTree(object):
    def __init__(self, l, d, request):
        self.l = l
        self.d = d
        self.req = request

    def checkExecuteArgs(self, node):
        return node

    def checkExecuteRequestArgs(self, node):
        l = self.l
        req = self.req
        node = self.RewriteExecuteRequestArgs().visit(node)
        return node

    class RewriteExecuteRequestArgs(ast.NodeTransformer):
        def visit_Call(self, node):
            if isinstance(node.func, ast.Attribute) and node.func.attr == 'execute':
                if node.func.value.id in l:
                    for arg in node.args:
                        if arg.id in d.keys():
                            request_attrs = d[arg.id]
                            print(request_attrs)
                            print("request.params['ID']: ", request.params["ID"])
                            # requestのうちs4を実行して変更？
                            # 関数を一つ入れる、その時に引数をもらって検証？
                            # その関数の中身を引数の関数にする
                            # request_attrs = {params: ["ID", "Password"]}
                            # 検証(request.params["ID"]との比較)
                            return node
            #for target in node.targets:
            #    if target.id in l:
            #        print(ast.dump(node))
            #        RewriteExecute().visit(node)
            #nodeを変更？検証？
            return node

def checkArg(arg, request_attr, check_func):
    Hoge = check_func(arg, request_attr, **argv):


if __name__=="__main__":
    tree = ast.parse(source)
    request = Request()
    rerequest = Rerequest(request)
    exec(compile(ast.fix_missing_locations(tree), filename="<ast>", mode="exec"))
    ret = func1(request)
    print(ret)
    print()

    l = findcursor.searchCursor(tree)
    tree = searchExecuteArgs(tree, l)
    search1 = checkAssignRequest()
    d = search1.searchAssign(tree)
    # {'s2': {'params': ['ID']}, 's3': {'params': ['Password']}, 's5': {'params': ['Password']}}
    # -> {..., 's5': {'params': ['ID', 'Password']}}
    search2 = addAssign()
    d = search2.addAssign(tree, d)
    print("l: ", end="")
    print(l, end = ", d: ")
    print(d)

    tree_fixer = FixTree(l, d, request)
    tree = tree_fixer.checkExecuteRequestArgs(tree)
    # cur.executeを探す
    # 変数を探す
    #
    exec(compile(ast.fix_missing_locations(tree), filename="<ast>", mode="exec"))
    ret = func1(request)
    print(ret)
