# request -> rererequest
import sqlite3
import ast

class Request:
    def __init__(self):
        self.params = {"ID": "1 or 1 = 1 order by ID desc;--", "Password":""}

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
def func1(request):
    conn = sqlite3.connect("test1.db")
    cur = conn.cursor()

    s1 = "select * from table1"
    s2 = " where ID = {}".format(request.params.get("ID"))
    s3 = " and Password = {}".format(request.params["Password"])

    s4 = s2
    s5 = s3
    #cur.execute(s1+s2+s3)
    cur.execute("select * from table1 where ID = {} and Password = {}".format(request.params.get("ID"), request.params.get("Password")))
    data = cur.fetchone()
    conn.commit()
    print("Params: {}".format(request.params))
    return "Return: Hello, " + data[1] + ". Your ID is " + data[0]
'''

class RewriteRequest(ast.NodeTransformer):
    def visit_Name(self, node):
        if node.id == "request":
            new_node = ast.Name(id="rerequest", ctx=node.ctx)
            return ast.copy_location(new_node, node)
        return node

if __name__=="__main__":
    tree = ast.parse(source)
    #print(ast.dump(tree))
    request = Request()
    rerequest = Rerequest(request)
    exec(compile(ast.fix_missing_locations(tree), filename="<ast>", mode="exec"))
    ret = func1(request)
    print(ret)
    print()

    tree2 = RewriteRequest().visit(tree)
    exec(compile(ast.fix_missing_locations(tree2), filename="<ast>", mode="exec"))
    ret2 = func1(request)
    print(ret2)
    print()
