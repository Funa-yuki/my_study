import ast
# リストを見つける[cur]->executeな引数を見つける
def searchExecuteArgs(node, l):
    for a in ast.walk(node):
        if isinstance(a, ast.Call) and isinstance(a.func, ast.Attribute):
            if isinstance(a.func.value, ast.Name) and a.func.value.id in l:
                if a.func.attr == "execute":
                    #print(ast.dump(a))
                    for arg in a.args:
                        print(ast.dump(arg))

class reWriteExecuteRequestArgs(ast.NodeTransformer):
    def visit_Name(self, node):
        if node.id == "request":
            
