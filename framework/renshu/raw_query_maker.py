import sqlite3

conn = sqlite3.connect('test1.db')
c = conn.cursor()

class Request(object):
    def __init__(self, params):
        self.params = params

request = Request({"ID": "1 or 1 = 1 order by ID desc;--", "Password": ""})

def route(func, path, method="GET"): pass

@route("/", "GET")
def doLogin(request):
    select_query = "select * from table1"
    i = 0
    for k, v in request.params.items():
        if i == 0:
            select_query += " where {} = {}".format(k, v)
            i += 1
        else:
            select_query += " and {} = {}".format(k, v)

    print(select_query)
    try:
        c.execute(select_query)
        data = c.fetchone()
    except:
        data = None

    return "<a2>こんにちは, {}</a2>".format(data[1]) if data else "<a2>IDかパスワードが正しくありません</a2>"


print(doLogin(request))
