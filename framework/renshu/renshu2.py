import ast
from copy import copy

class Visitor1(ast.NodeVisitor):
    def __init__(self):
        self.vars = {}

    def visit_Call(self, node):
        try:
            if node.func.value.id in ["c", "cur", "cursor"] and node.func.attr == "execute":
                #print(ast.dump(node.args[0]))
                i = 0
                n = node.args[0]
                while True:
                    #print(ast.dump(n))
                    try:
                        print(n.right.id)
                        n = n.left
                    except:
                        print(n.id)
                        break
        except: pass

    def visit_Assign(self, node):
    #    print(node.targets[0].id)
        self.FindFormat(node.value) # find s = "hoge {}".format(request.params[ID])
        self.FindRequest(node) # s = request.params["ID"]
        return node

    def FindFormat(self, node):
        try:
            if node.func.attr == "format":
                #print(ast.dump(node.args[0]))
                return node.args[0]
        except:
            return node

    def FindRequest(self, node):
        try:
            if node.value.value.value.id == "request" and node.value.value.attr == "params":
                #print(ast.dump(node.value))
                return node
        except:
            #print(ast.dump(node.value))
            pass
            return node


class RewriteQuery(object):
    def __init__(self, node):
        self.node = node
        self.calls = []
        self.imports = []
        self.aug_assigns = []
        self.db_assigns = []
        self.params = {}
    def find(self, attr):
        l = []
        for t in ast.walk(tree):
            if isinstance(t, attr):
                l.append(t)
        return l

    def findCall(self):
        self.calls = copy(self.find(ast.Call))

    # importであるast命令を探す
    def findImport(self):
        self.imports = copy(self.find(ast.Import))

    def findAssign(self):
        self.assigns = copy(self.find(ast.Assign))

    def findAugAssign(self):
        self.aug_assigns = copy(self.find(ast.AugAssign))

     # dbを実行できるインスタンスを探す
    def findDatabaseAssign(self):
        for a in self.assigns:
            if isinstance(a.value, ast.Call) and isinstance(a.value.func.value, ast.Name):
                if type(a.value.func.value.id) is str:
                    s = a.value.func.value.id
                    val = a.value.func
                    if (s == 'sqlite3' and val.attr == 'connect')or (s in self.db_assigns and val.attr == 'cursor'):
                        self.db_assigns.append(a.targets[0].id)

    # dbを実行したast.Callオブジェクトから用いられた引数を探す
    def findArgsInDatabaseExecute(self):
        for call_node in self.calls:
            #print(ast.dump(call_node))
            if isinstance(call_node.func, ast.Attribute):
                call_func = call_node.func
                if isinstance(call_func.value, ast.Name) and call_func.value.id in self.db_assigns and call_func.attr == "execute":
                    if len(call_node.args) == 1:
                        if isinstance(call_node.args[0], ast.Name):
                            print(call_node.args[0].id) # c.execute(arg)
                            pass
                        elif isinstance(call_node.args[0], ast.BinOp):
                            add_args = call_node.args[0]
                            print(ast.dump(call_node.args[0]))
                        else:
                            for arg in call_node.args:
                                print(ast.dump(arg))
                        print("")


class Request(object):
    def __init__(self, params):
        self.params = params

#conn = sqlite3.connect('test1.db')
#c = conn.cursor()
request = Request({"ID": "1 or 1 = 1 order by ID desc;--", "Password": ""})
request2 = Request({"ID":"1", "Password": "password"})

source = '''
import sqlite3
conn = sqlite3.connect('test1.db')
c = conn.cursor()

select_query = "select * from table1"
s1 = "select * from table1"
s2 = " where ID = {}".format(request2.params["ID"])
s3 = " and Password = " + request2.params["Password"]
i = 0
for k, v in request.params.items():
    if request.params.get(k):
        if i == 0:
            select_query += " where {} = {}".format(k, v)
            i += 1
        else:
            select_query += " and {} = {}".format(k, v)

c.execute(select_query)
data = c.fetchone()
conn.execute(s1+s2+s3)
#c.execute(s1, s2)
s1 += s2
s1 += s3
c.execute(s1)
c.execute("select * from table1 where ID = ?", (request.params["ID"], ))
data2 = c.fetchone()
c.execute("select * from table1 where ID = {}".format(request2.params["ID"]))
data3 = c.fetchone()
#print(data, data2, data3)
s4 = "Hello, {}, Your ID is {}.".format(data3[1], request2.params["ID"])
'''

source2 = '''
s = "s1 {}".format(request.params["ID"])
'''

tree = ast.parse(source)

ins = RewriteQuery(tree)
ins.findImport()
ins.findAssign()
ins.findAugAssign()
ins.findDatabaseAssign()
ins.findCall()
ins.findArgsInDatabaseExecute()

'''
for imp in ins.imports:
    print(ast.dump(imp))

for l in ins.calls:
    print(ast.dump(l))
'''
for a in ins.assigns:
    print(ast.dump(a))
for a in ins.aug_assigns:
    print(ast.dump(a))
 #実はast.Exprがキモ？
exec(compile(tree, filename="<ast>", mode="exec"))
print(s4)
