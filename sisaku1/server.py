from app import *
from front import template
import sqlite3

@app.route("^/$", "GET")
def index(request):
    return template("index.html")

@app.route("^/login$", "GET")
def login(request):
    return template("login.html")

@app.route("^/login$", "POST")
def do_login(request):
    id = request.forms.get("id")
    password = request.forms.get("password")
    if check_auth(request=request, id=id, password=password, dbname="test.sqlite3"):
        return template("home.html") #redirectする必要がある
    else:
        return template("login.html")

#for sql injection experiment
@app.route("/sql", "GET")
@app.funcFixer.fix("")
def access_sql(request):
    conn = sqlite3.connect('test.sqlite3')
    cur = conn.cursor()
    id = request.forms.get("id")
    password = request.forms.get("password")
    #cur.execute(query)
    id = "' union select * from admin ;--"
    password = ""
    query = "select * from test1 where id = '{}' and password = '{}'".format(id, password)
    print(query)

    if not id:
        return 'form'
    else:
        cur.execute(query)
        data = cur.fetchone()
        if data:
            username= data[0]
            password = data[1]
            return "Hello, {}. Your password is {}".format(username, password)
        return "Again"

@app.route("^/home$")
def home(request):
    if check_auth(request=request):
        print("hoge")
        return template("home.html")
    else:
        return template("login.html") #redirectする必要があある

@app.route("/vuln_home$")
def vuln_home(request):
    check_auth(request=request)
    return template("home.html")

if __name__=="__main__":
    port = 8000
    app.run(port=8000)
