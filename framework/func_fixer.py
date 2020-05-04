import re
import ast
import inspect
import copy

class FuncFixer(object):
    def __init__(self):
        self.funcs = {}

    #{"func1": func1, ...}
    def addNodeFixer(self, check):
        def decorator(check_func):
            func_name = check_func.__name__
            self.funcs[func_name] = check_func
            return check_func
        return decorator(check)

    # astを受け取って、このデコレータ部分を削除して返す
    def removeDecoratorFromAst(self, node):
        class RemoveFixDecoraterList(ast.NodeTransformer):
            def visit_FunctionDef(self, node):
                if node.decorator_list:
                    new_decorator_list = copy.deepcopy(node.decorator_list)
                    print(new_decorator_list)
                    print(ast.dump(new_decorator_list[0]))
                    print(ast.dump(new_decorator_list[1]))
                    num = 0
                    while(new_decorator_list or num < len(new_decorator_list)):
                        #ここの条件をあとで考える
                        if num == num:
                            new_decorator_list.pop(num)
                        else:
                            num += 1

                    new_node = ast.FunctionDef(
                        name=node.name,
                        args=node.args,
                        body=node.body,
                        decorator_list=new_decorator_list,
                        returns=node.returns
                    )
                    return ast.copy_location(new_node, node)
                return node

        new_node = RemoveFixDecoraterList().visit(node)

        return new_node

    '''
    #code_example
    @fixer.check("func1")
    def index(s):
        print(s)
        return s
    '''
    def fixIndent(self, text):
        indent = 0
        fixed_text = ''
        lines = text.splitlines()
        for num in range(len(lines)):
            if num is 0 and lines[0][0] is ' ':
                for character in lines[num]:
                    if character is ' ':
                        indent += 1
                        print("hoge")
            fixed_text += lines[num].replace(' '*indent, '', 1)
            fixed_text += '\n'
        return fixed_text


    def fix(self, func_name):
        def decorator(callback):
            callback_name = callback.__name__
            def wrapper(request):
                source = inspect.getsource(callback)
                source = self.fixIndent(source)
                callback_ast = ast.parse(source)
                # ast上のfixerなデコレータを消す
                callback_ast = self.removeDecoratorFromAst(callback_ast)
                fixingFunc = self.funcs.get(func_name)
                callback_ast = fixingFunc(callback_ast)
                exec(compile(ast.fix_missing_locations(callback_ast), filename="<ast>", mode="exec"))
                new_callback = locals().get(callback_name)
                return new_callback(request)
            return wrapper
        return decorator

    def check2(self, func_name, callback):
        callback_ast = ast.parse(inspect.getsource(callback))
        check_func = self.funcs.get(func_name)
        callback_ast = check_func(callback_ast)
        exec(ast.fix_missing_locations(callback_ast))
        return callback

class RewritePrintToReversePrint(ast.NodeTransformer):
    def visit_Name(self, node):
        if node.id is 'print':
            new_node = ast.Name(
                id='reversePrint',
                ctx=ast.Load()
            )
            return ast.copy_location(new_node, node)
        return node

if __name__=='__main__':
    fixer = FuncFixer()

    @fixer.addNodeFixer
    def func1(node):
        node = RewritePrintToReversePrint().visit(node)
        return node

        #@app.route(path="/", method="GET")
    @fixer.fix("func1")
    def index(s):
        print(s)
        return s

#print(index)
# index("hoge")->fixer.fix("func1", new_callback)("hoge")
    print(inspect.getsource(index))
    index("dexif")


'''
@fixer.check(func_name="func1")
def index():
    print("hoge")
    return "hoge"
'''
