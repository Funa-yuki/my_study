import ast
import inspect

class Rewrite(ast.NodeTransformer):
    def visit_Name(self, node):
        if node.id is 'print':
            new_node = ast.Name(
                id='reversePrint',
                ctx=ast.Load()
            )
            return ast.copy_location(new_node, node)
        return node

def normalPrint(s):
    print(s)

def reversePrint(s):
    print(s[::-1])

def fix(node):
    exec(compile(ast.fix_missing_locations(node), filename="<ast>", mode="exec"))
    print(locals().get('normalPrint'))
    print(globals().get('normalPrint'))
    localargs = locals()
    f = localargs.get('normalPrint')
    return f

callback = normalPrint

callback_txt = inspect.getsource(callback)
callback_tree = ast.parse(callback_txt)

tree = Rewrite().visit(callback_tree)
normalPrint = fix(tree)

normalPrint("hoge")
