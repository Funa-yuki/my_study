import inspect
import ast

source='''
@fixer.fix("func1")
@fixer.fix("func2")
def index(s):
    print(s)
    return s
'''

print(ast.dump(ast.parse(source)))

#FunctionDef(name='index', args=arguments(args=[arg(arg='s', annotation=None)], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]), body=[Expr(value=Call(func=Name(id='print', ctx=Load()), args=[Name(id='s', ctx=Load())], keywords=[])), Return(value=Name(id='s', ctx=Load()))], decorator_list=[Call(func=Attribute(value=Name(id='fixer', ctx=Load()), attr='fix', ctx=Load()), args=[Str(s='func1')], keywords=[])], returns=None)
#FunctionDef(name='index', args=arguments(args=[arg(arg='s', annotation=None)], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]), body=[Expr(value=Call(func=Name(id='print', ctx=Load()), args=[Name(id='s', ctx=Load())], keywords=[])), Return(value=Name(id='s', ctx=Load()))], decorator_list=[], returns=None)
