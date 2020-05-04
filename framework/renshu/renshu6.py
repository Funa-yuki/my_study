import ast

class Request:
    def __init__(self):
        self.params = {"ID": "1 or 1 = 1 order by ID desc;--", "Password":"hogehoge"}


source = '''
def func1():
    request = Request()
    s4 = "select * from table1"
    i = 0
    for k, v in request.params.items():
        if v:
            if i == 0:
                s4 += " where {} = {}".format(k, v)
                i += 1
            else:
                s4 += " and {} = {}".format(k, v)

        return s4
'''

class FindForRequest:
    def __init__(self):
        pass

    def searchRequestIter(self, node):
        for a in ast.walk(node):
            if isinstance(a, ast.For):
                request_iter = self.searchIter(a.iter)
                print(request_iter)
                # 何を変更するかの話か
                # for文である => iterがrequest かつ　iter

    def searchIter(self, iter_node):
        for a in ast.walk(iter_node):
            if isinstance(a, ast.Name) and a.id == "request":
                return iter_node
        return None

if __name__=="__main__":
    tree = ast.parse(source)
    f = FindForRequest()
    f.searchRequestIter(tree)
    exec(compile(tree, filename="<ast>", mode="exec"))
    print(func1())
