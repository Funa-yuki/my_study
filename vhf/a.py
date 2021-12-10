import ast
print(ast.dump(ast.parse('d = a if b else c', mode='exec')))

# Expression(
#     body=Call(
#         func=Attribute(
#             value=Name(id='conn', ctx=Load()),
#             attr='cursor',
#             ctx=Load()),
#             args=[],
#             keywords=[]))

# Expression(
#     body=Call(
#         func=Name(id='print',ctx=Load()),
#             args=[Constant(value='moji', kind=None)], keywords=[]))


# Expression(
#     body=Call(
#         func=Name(id='print', ctx=Load()),
#         args=[Constant(value='moji', kind=None)],
#         keywords=[keyword(arg='end', value=Constant(value='mm', kind=None))]))



# Module(
#     body=[Expr(value=Call(func=Name(id='print', ctx=Load()), args=[Name(id='add', ctx=Load())], keywords=[keyword(arg='end', value=Constant(value='mm', kind=None))])),
#     Assign(targets=[Name(id='a', ctx=Store())], value=Name(id='b', ctx=Load()), type_comment=None)], type_ignores=[])


# Call(func=Name(id='tmpl', ctx=Load()), args=[Constant(value='index.html', kind=None)], keywords=[])
# Call(func=Name(id='tmpl', ctx=Load()), args=[Constant(value='database.html', kind=None)], keywords=[keyword(arg='action', value=Constant(value='None', kind=None)), keyword(arg='result', value=Constant(value='None', kind=None))])
# Call(func=Attribute(value=Name(id='sqlite3', ctx=Load()), attr='connect', ctx=Load()), args=[Constant(value='database.sqlite3', kind=None)], keywords=[])
# Call(func=Attribute(value=Name(id='conn', ctx=Load()), attr='cursor', ctx=Load()), args=[], keywords=[])
# Call(func=Attribute(value=Attribute(value=Name(id='request', ctx=Load()), attr='forms', ctx=Load()), attr='get', ctx=Load()), args=[Constant(value='action', kind=None)], keywords=[])
# Call(func=Attribute(value=Constant(value='{action}', kind=None), attr='format', ctx=Load()), args=[], keywords=[keyword(arg='action', value=Subscript(value=Name(id='action', ctx=Load()), slice=Index(value=Constant(value=0, kind=None)), ctx=Load()))])
# Call(func=Attribute(value=Name(id='cur', ctx=Load()), attr='execute', ctx=Load()), args=[Name(id='query', ctx=Load())], keywords=[])
# Call(func=Attribute(value=Name(id='cur', ctx=Load()), attr='fetchall', ctx=Load()), args=[], keywords=[])
# Call(func=Attribute(value=Name(id='conn', ctx=Load()), attr='commit', ctx=Load()), args=[], keywords=[])
# Call(func=Attribute(value=Name(id='conn', ctx=Load()), attr='close', ctx=Load()), args=[], keywords=[])
# Call(func=Name(id='tmpl', ctx=Load()), args=[Constant(value='database.html', kind=None)], keywords=[keyword(arg='action', value=Name(id='action', ctx=Load())), keyword(arg='result', value=Name(id='data', ctx=Load()))])


# Module(body=[FunctionDef(name='index',    args=arguments(posonlyargs=[], args=[arg(arg='request', annotation=None, type_comment=None)], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]), body=[Return(value=Call(func=Name(id='tmpl', ctx=Load()), args=[Constant(value='index.html', kind=None)], keywords=[]))], decorator_list=[], returns=None, type_comment=None)], type_ignores=[])
# Module(body=[FunctionDef(name='database', args=arguments(posonlyargs=[], args=[arg(arg='request', annotation=None, type_comment=None)], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]), body=[Return(value=Call(func=Name(id='tmpl', ctx=Load()), args=[Constant(value='database.html', kind=None)], keywords=[keyword(arg='action', value=Constant(value='None', kind=None)), keyword(arg='result', value=Constant(value='None', kind=None))]))], decorator_list=[], returns=None, type_comment=None)], type_ignores=[])
# Module(body=[FunctionDef(name='database', args=arguments(posonlyargs=[], args=[arg(arg='request', annotation=None, type_comment=None)], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]), body=[
#     Assign(targets=[Name(id='conn', ctx=Store())],   value=Call(func=Attribute(value=Name(id='sqlite3', ctx=Load()), attr='connect', ctx=Load()), args=[Constant(value='database.sqlite3', kind=None)], keywords=[]), type_comment=None), 
#     Assign(targets=[Name(id='cur', ctx=Store())],    value=Call(func=Attribute(value=Name(id='conn', ctx=Load()), attr='cursor', ctx=Load()), args=[], keywords=[]), type_comment=None), 
#     Assign(targets=[Name(id='action', ctx=Store())], value=Call(func=Attribute(value=Attribute(value=Name(id='request', ctx=Load()), attr='forms', ctx=Load()), attr='get', ctx=Load()), args=[Constant(value='action', kind=None)], keywords=[]), type_comment=None), 
#     Assign(targets=[Name(id='query', ctx=Store())],  value=Call(func=Attribute(value=Constant(value='{action}', kind=None), attr='format', ctx=Load()), args=[], keywords=[keyword(arg='action', value=Subscript(value=Name(id='action', ctx=Load()), slice=Index(value=Constant(value=0, kind=None)), ctx=Load()))]), type_comment=None), 
#     Expr(value=Call(func=Attribute(value=Name(id='cur', ctx=Load()), attr='execute', ctx=Load()), args=[Name(id='query', ctx=Load())], keywords=[])),
#     Assign(targets=[Name(id='data', ctx=Store())],   value=Call(func=Attribute(value=Name(id='cur', ctx=Load()), attr='fetchall', ctx=Load()), args=[], keywords=[]), type_comment=None), 
#     Expr(value=Call(func=Attribute(value=Name(id='conn', ctx=Load()), attr='commit', ctx=Load()), args=[], keywords=[])), 
#     Expr(value=Call(func=Attribute(value=Name(id='conn', ctx=Load()), attr='close', ctx=Load()), args=[], keywords=[])), 
#     Return(value=Call(func=Name(id='tmpl', ctx=Load()), args=[Constant(value='database.html', kind=None)], keywords=[keyword(arg='action', value=Name(id='action', ctx=Load())), keyword(arg='result', value=Name(id='data', ctx=Load()))]))], decorator_list=[], returns=None, type_comment=None)], type_ignores=[])


# FunctionDef(name='index', args=arguments(posonlyargs=[], args=[arg(arg='request', annotation=None, type_comment=None)], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]),
#  body=[
#      ImportFrom(module='bottle', names=[alias(name='jinja2_template', asname='tmpl')], level=0), 
#      Return(value=Call(func=Name(id='tmpl', ctx=Load()), args=[Constant(value='index.html', kind=None)], keywords=[]))], decorator_list=[], returns=None, type_comment=None)
# FunctionDef(name='database', args=arguments(posonlyargs=[], args=[arg(arg='request', annotation=None, type_comment=None)], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]),
#  body=[
#      ImportFrom(module='bottle', names=[alias(name='jinja2_template', asname='tmpl')], level=0), 
#      Return(value=Call(func=Name(id='tmpl', ctx=Load()), args=[Constant(value='database.html', kind=None)], keywords=[keyword(arg='action', value=Constant(value='None', kind=None)), keyword(arg='result', value=Constant(value='None', kind=None))]))], decorator_list=[], returns=None, type_comment=None)
# FunctionDef(name='database', args=arguments(posonlyargs=[], args=[arg(arg='request', annotation=None, type_comment=None)], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]),
#  body=[
#      ImportFrom(module='bottle', names=[alias(name='jinja2_template', asname='tmpl')], level=0), 
#      Import(names=[alias(name='sqlite3', asname='sql3')]), 
#      Assign(targets=[Name(id='conne', ctx=Store())], value=Call(func=Attribute(value=Name(id='sql3', ctx=Load()), attr='connect', ctx=Load()), args=[Constant(value='database.sqlite3', kind=None)], keywords=[]), type_comment=None), 
#      Assign(targets=[Name(id='curs', ctx=Store())], value=Call(func=Attribute(value=Name(id='conne', ctx=Load()), attr='cursor', ctx=Load()), args=[], keywords=[]), type_comment=None), 
#      Assign(targets=[Name(id='action', ctx=Store())], value=Call(func=Attribute(value=Attribute(value=Name(id='request', ctx=Load()), attr='forms', ctx=Load()), attr='get', ctx=Load()), args=[Constant(value='action', kind=None)], keywords=[]), type_comment=None), 
#      Assign(targets=[Name(id='query', ctx=Store())], value=Call(func=Attribute(value=Constant(value='{action}', kind=None), attr='format', ctx=Load()), args=[], keywords=[keyword(arg='action', value=Subscript(value=Name(id='action', ctx=Load()), slice=Index(value=Constant(value=0, kind=None)), ctx=Load()))]), type_comment=None), 
#      Expr(value=Call(func=Attribute(value=Name(id='curs', ctx=Load()), attr='execute', ctx=Load()), args=[Name(id='query', ctx=Load())], keywords=[])), 
#      Assign(targets=[Name(id='data', ctx=Store())], value=Call(func=Attribute(value=Name(id='curs', ctx=Load()), attr='fetchall', ctx=Load()), args=[], keywords=[]), type_comment=None), 
#      Expr(value=Call(func=Attribute(value=Name(id='conne', ctx=Load()), attr='commit', ctx=Load()), args=[], keywords=[])), 
#      Expr(value=Call(func=Attribute(value=Name(id='conne', ctx=Load()), attr='close', ctx=Load()), args=[], keywords=[])), 
#      Return(value=Call(func=Name(id='tmpl', ctx=Load()), args=[Constant(value='database.html', kind=None)], keywords=[keyword(arg='action', value=Name(id='action', ctx=Load())), keyword(arg='result', value=Name(id='data', ctx=Load()))]))], decorator_list=[], returns=None, type_comment=None)







