import sqlite3
import re
import ast

class Fixer(object):
    def __init__(self):
        self.fixers = []

    def addNodeFixer(self, check):
        def decorator(check_func):
            self.fixers.append(check_func)
            return check_func
        return decorator(check)

default_fixers = Fixer()

### default fixers
class InsertQueryChecker(ast.NodeTransformer):
    def visit_Call(self, node):
        #Call(
        #func=Attribute(
        #value=Name(id='cur', ctx=Load()), attr='execute', ctx=Load()), args=[Name(id='query', ctx=Load()
        #cur.execute()を探す->引数を変更する
        child_node = node.func
        if isinstance(child_node, ast.Attribute) and isinstance(child_node.value, ast.Name) and child_node.value.id is 'cur':
            if child_node.attr is 'execute':
                new_args = []
                for arg in node.args:
                    #Call(func=Attribute(value=Name(id='cur', ctx=Load()), attr='execute', ctx=Load()), args=[Name(id='query', ctx=Load())], keywords=[])
                    new_arg = ast.Call(
                                func=(ast.Name(id='escape_query', ctx=ast.Load())),
                                args=[arg],
                                keywords=[]
                            )
                    new_args.append(new_arg)
                new_node = ast.Call(
                    func=node.func,
                    args=new_args,
                    keywords=node.keywords
                )
                new_node = ast.copy_location(new_node, node)
                return new_node
        return node

@default_fixers.addNodeFixer
def check_query(node):
    new_node = InsertQueryChecker().visit(node)
    return new_node
###


##### コールバック関数ヘルパーのヘルパー群　#####
def reversePrint(s):
    print(s[::-1])

def escape_query(query):
    escaped_query = ""
    queries = query.split(";")
    for q in queries:
        if escape_special_query(q):
            escaped_query += escape_special_query(q)
            escaped_query += "; "
    print(query)
    print(escaped_query)
    return escaped_query

def escape_special_query(query):
    # not where
    if not re.search(r"where", query):
        return ""
    # escape drop
    if re.match(r"drop", query):
        return ""
    return query

def has_admin_account(id=None, password=None, db="sqlite3", dbname=None):
    # 検証関数
    if id is None or password is None or dbname is None:
        return False
    if db is "sqlite3":
        if dbname is None:
            return False
        conn = sqlite3.connect(dbname)
        cur = conn.cursor()
        cur.execute("select * from test1 where id=? and password=?", (id, password,))
        if cur.fetchone():
            return True
    return False

if __name__=="__main__":

    source = '''
def access_sql(request=None):
    id = "Tanaka'; select * from user;drop user;--"
    password = "Tanaka_Pass"
    #cur.execute(query)
    query = "select * from test1 where id = '{}' and password = '{}'".format(id, password)
    if not id:
        return 'form'
    else:
        cur.execute(query)
        data = cur.fetchone()
        if data:
            username= data[0]
            password = data[1]
        return "Hello, {}. Your password is {}".format(username, password)
    '''

    conn = sqlite3.connect("test.sqlite3")
    cur = conn.cursor()
    node = ast.parse(source)
    new_node = InsertQueryChecker().visit(node)
    exec(compile(ast.fix_missing_locations(new_node), filename="<ast>", mode="exec"))
    print(access_sql("req"))

    '''
    for i in range(10):
        if i % 2 == 0:
            print(check_auth(id="hoge", password="fuga", dbname="test.sqlite3"))
        else:
            print(check_auth(id="Tanaka", password="Tanaka_Pass", dbname="test.sqlite3"))
    '''
