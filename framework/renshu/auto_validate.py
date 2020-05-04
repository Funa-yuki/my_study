import ast

class RewriteDecorator(ast.NodeTransformer):
    def visit_FunctionDef(self, node):
        decorators = node.decorator_list
        if decorators:
            print('decorated: {}'.format(node.name))
            for call in decorators:
                print(call.func.id)
            print('-' * 32)
        return node
        

class RewriteName(ast.NodeTransformer):

    def visit_Name(self, node):
        return ast.Subscript(
            value=ast.Name(id='data', ctx=ast.Load()),
            slice=ast.Index(value=ast.Constant(value=node.id)),
            ctx=node.ctx
        )

if __name__ == "__main__":
    FILENAME = "raw_query_maker.py"
    with open(FILENAME, "r") as f:
        source = f.read()

    tree = ast.parse(source)
    print(ast.dump(RewriteDecorator.visit(tree)))
