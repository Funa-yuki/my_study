import ast

class Request:
    def __init__(self, params):
        self.params = params

class AssignRequest(object):
    def __init__(self, requests=None, items=None):
        self.request_params = requests
        self.items = items

request = Request({"ID":"1", "Password":"password"})

# test1は、c.execute(s1+s2+s3)
# s2とs3をリクエスト側にハードコーディングで入れておく
#from sqlite3 import connectを後で考慮
test1 = '''
import inspect, sqlite3 as sql3
import MySQLdb
conn = sql3.connect("test1.db")
cur = conn.cursor()
cur.execute(s1+s2+s3)
conn.commit()
'''

class SearchDbExecute:
    def __init__(self):
        self.relational_db_modules = ["sqlite3", "MySQLdb"]

    def searchImportSQL(self, node):
        l = []
        for a in ast.walk(node):
            if isinstance(a, ast.Import):
                for n in a.names:
                    if n.name in self.relational_db_modules:
                        l.append(n.name) if not n.asname else l.append(n.asname)
        return l # self.relational_db_modulesからimportを検索

    #attrがconnectな代入からcursorできるidのリストを返す
    def searchCursor(self, node):
        l = []
        import_list = self.searchImportSQL(node)
        for n in ast.walk(node):
            if isinstance(n, ast.Assign) and isinstance(n.value, ast.Call):
                if isinstance(n.value.func.value, ast.Name) and (n.value.func.value.id in import_list or n.value.func.value.id in l):
                    l.append(n.targets[0].id)
        return l #cursorもしくはそれをassignで利用した変数のid

    def searchExecute(self, node):
        l = []
        cursors = self.searchCursor(node)
        for a in ast.walk(node):
            if isinstance(a, ast.Call) and isinstance(a.func, ast.Attribute):
                if isinstance(a.func.value, ast.Name) and a.func.value.id in cursors:
                    if a.func.attr == "execute":
                        for arg in a.args:

                            print(ast.dump(arg))
                        l.append(a)
        return l

findcursor = SearchDbExecute()
#test_code
if __name__=="__main__":
    f = SearchDbExecute()
    el = f.searchExecute(ast.parse(test1))
    print(ast.dump(el[0]))
