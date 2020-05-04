import ast

source = '''
def func1():
    s = 0
    for inter in range(20):
        s += inter
        print(s)
'''

class Request:
    def __init__(self):
        self.request_params = ["s1", "s2"]
        self.items = ["v"]

request = Request()


#クラスを小さく分割すればいいのか
#assignのみで変更
#for文
class OpTransformer(ast.NodeTransformer):
    def visit_Assign(self, node):
        if type(node.value) is not str:
            new_node = ast.Assign(
                targets=[ast.Name(id=node.targets[0].id, ctx=node.targets[0]).ctx],
                value=ast.Str(s='')
            )
            return ast.copy_location(new_node, node)
        return node

    def visit_AugAssign(self, node):
        print(request.request_params)
        if isinstance(node, ast.AugAssign):
            call_str = ast.Call(func=ast.Name(id="str", ctx=ast.Load()), args=[node.value], keywords=[])
            new_node = ast.AugAssign(
                    target=ast.Name(id=node.target.id, ctx=node.target.ctx),
                    op=node.op,
                    value=call_str
                )
            return ast.copy_location(new_node, node)
        return node

    #new_node = self.fixCallFormat(node)
    #new_node = ast.Assign(, ..., value=new_node<-call以下)
    def fixCallFormat(self, node_Call):
        #ast.Call(node)みたいにして変換
        return new_node

    def fixFormat(self, node_Call):
        #new_node = ast.Call(...)
        return new_node


def reverse_print(s):
    print(s[::-1])

class RewritePrintReverse(object):
    def reverse(self, node):
        node = OpTransformer().visit(node)
        node = self.RewritePrint().visit(node)
        return node


    class RewritePrint(ast.NodeTransformer):
        def visit_Name(self, node):
            if node.id is 'print':
                new_node = ast.Name(
                    id='reverse_print',
                    ctx=ast.Load()
                    )
                return ast.copy_location(new_node, node)
            return node



tree = ast.parse(source)
#print(ast.dump(tree))
exec(compile(ast.fix_missing_locations(tree), filename="<ast>", mode="exec"))
func1()

reverse_print_instance = RewritePrintReverse()
tree = reverse_print_instance.reverse(tree)
#print(ast.dump(new_node))
exec(compile(ast.fix_missing_locations(tree), filename="<ast>", mode="exec"))
func1()
