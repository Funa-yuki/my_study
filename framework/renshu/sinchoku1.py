#!/usr/bin/env python3
# Call(attr=(id='execute'))から引数を取り出す
import ast
from renshu5 import findcursor

class Request:
    def __init__(self):
        self.params = {"ID": "1 or 1 = 1 order by ID desc;--", "Password":"hogehoge"}

class ReRequest:
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

class SearchRequest(object):
    def __init__(self):
        self.params = []

    #for文の場合、他の条件による一致が必要
    def searchRequestInAssign(self, node):
        for a in ast.walk(node):
            if isinstance(a, ast.Assign) or isinstance(a, ast.AugAssign):
                ans = self.searchNamedRequest(a)
                if ans: self.params.append(ans)
        return self.params

    #search iterator
    def searchRequestInFor(self, node):
        return self.params

    def searchNamedRequest(self, node):
        for a in ast.walk(node):
            if isinstance(a, ast.Name) and a.id == 'request':
                if isinstance(node, ast.Assign):
                    return node.targets[0].id
                elif isinstance(node, ast.AugAssign):
                    return node.target.id
        return None

class RewriteNameToReRequest(ast.NodeTransformer):
    def visit_Name(self, node):
        if node.id == "request":
            new_node = ast.Name(id="rerequest", ctx=node.ctx)
            return new_node
        return node

class RewriteAssignAndAugAssign(ast.NodeTransformer):
    def visit_Assign(self, node):
        if node.targets[0].id in l:
            #print("{} in {}".format(node.targets[0].id, l))
            new_node = RewriteNameToReRequest().visit(node)# 新しいクラスで変更
            return ast.copy_location(new_node, node)
        return node

    def visit_AugAssign(self, node):
        if node.target.id in l:
            #print("{} in {}".format(node.targets[0].id, l))
            new_node = RewriteNameToReRequest().visit(node)# 新しいクラスで変更
            return ast.copy_location(new_node, node)
        return node

# c.execute("".format(request.params["ID"]))を変更
# c.execute("".format(s1, s2, s3))
# c.executeを探す->変数を探す->

source = '''
import sqlite3

def func1(request):
    conn = sqlite3.connect("test1.db")
    cur = conn.cursor()

    s1 = "select * from table1"
    s2 = " where ID = {}".format(request.params.get("ID"))
    s3 = ""
    s3 += " and Password = {}".format(request.params["Password"])

    s4 = s2
    s5 = s3
    cur.execute(s1+s4+s5)
    #conn.commit()
    #print("Query: ", end="")
    #print("select * from table1 where ID = {} and Password = {}".format(request.params.get("ID"), request.params.get("Password")))
    #cur.execute("select * from table1 where ID = {} and Password = {}".format(request.params.get("ID"), request.params.get("Password")))

    print("Query: " + s1+s4+s5)
    try:
        data = cur.fetchone()
        conn.commit()
        return "Return: Hello, " + data[1] + ". Your ID is " + data[0]
    except:
        return "Error"
'''

#s2とs3が取れればok->for文とかだと他にも処理が必要？

#test_code
if __name__=="__main__":
    test1 = ast.parse(source)
    s = SearchRequest()
    l = s.searchRequestInAssign(test1)
    #l += s.searchRequestInFor(test1)
    print(l)
    request = Request()
    rerequest = ReRequest(request)

    exec(compile(ast.fix_missing_locations(test1), filename="<ast>", mode="exec"))
    ret = func1(request)
    print(ret)
    print()

    test2 = RewriteAssignAndAugAssign().visit(test1)
    exec(compile(ast.fix_missing_locations(test2), filename="<ast>", mode="exec"))
    ret2 = func1(request)
    print(ret2)
    print()
