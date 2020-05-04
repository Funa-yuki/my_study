import ast

class Request:
    def __init__(self, d):
        self.params = d

d = {"ID": "1", "Password":"password"}
request = Request(d)

source = '''
l = ["select * from table1", " where ID = 1", " and Password = password"]
d = {"ID": "1", "Password":"password"}
s = "select * from table1"
i = 0
for k, v in request.params.items():
    if v:
        if i == 0:
            s += " where {} = {}".format(k, v)
            i += 1
        else:
            s += " and {} = {}".format(k, v)

print(s)

'''

class NodeVisitor:
    def __init__(self):
        self.request_params = []

    def findItems(self, node):
        for a in ast.walk(node):
            if isinstance(ast.For):
                if isinstance(a.iter.func, ast.Attribute) and a.iter.func.attr == "items":
                    if isinstance(a.iter.func.value, ast.Name):
                        print(a.iter.func.value.id) # d
                        #for _, _ in d.items()
                    elif isinstance(a.iter.func.value, ast.Attribute) and isinstance(a.iter.func.value.value, ast.Name): #attrの底まで再起とか？
                        print(a.iter.func.value.attr) # params
                        print(a.iter.func.value.value.id) # request
                        #for _, _ in request.params.items()
                        print(a.target.elts[0].id) # k
                        print(a.target.elts[1].id) # v
                        self.request_params.append(a.target.elts[1].id)
                        # for k, v in request.params.items()
                        fixBody(a.body)

                elif isinstance(a.iter.func, ast.Name) and a.iter.func.id == "range":
                    print(a.iter.func.id) # range
                    # for _ in range()
            #print(a.iter.id) # ast.For
    def fixBody(body):
        for b in body:
            for n in ast.walk(b):
                if isinstance(n, ast.Name) and n.id in self.request_params:
                    print(ast.dump(b))

def fixBody(body, s):
    for b in body:
        for n in ast.walk(b):
            if isinstance(n, ast.AugAssign):
                print(ast.dump(n))
                if isinstance(n.value, ast.Call):
                    pass
                print()

tree = ast.parse(source)
for a in ast.walk(tree):
    if type(a) is ast.For:
        #print(ast.dump(a))
        if isinstance(a.iter, ast.Call):
            if isinstance(a.iter.func, ast.Attribute) and a.iter.func.attr == "items":
                if isinstance(a.iter.func.value, ast.Name):
                    print(a.iter.func.value.id) # d
                    #for _, _ in d.items()
                elif isinstance(a.iter.func.value, ast.Attribute) and isinstance(a.iter.func.value.value, ast.Name): #attrの底まで再起とか？
                    #print(a.iter.func.value.attr) # params
                    #print(a.iter.func.value.value.id) # request
                    #for _, _ in request.params.items()
                    #print(a.target.elts[0].id) # k
                    #print(a.target.elts[1].id) # v
                    # for k, v in request.params.items()
                    fixBody(a.body, a.target.elts[1].id)

            elif isinstance(a.iter.func, ast.Name) and a.iter.func.id == "range":
                print(a.iter.func.id) # range
                # for _ in range()
        #print(a.iter.id) # ast.For
        print()
#print(ast.dump(tree))
exec(compile(tree, filename="<ast>", mode="exec"))
