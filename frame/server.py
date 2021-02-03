from app import *

@app.route("^/$", "GET")
def index(request):
    print("hoge")
    return "INDEX"

@app.route("^/login$", "POST")
def login(request):
    return "LOGIN"

@app.route("^/login$", "GET")
def do_login(request):
    id = "admin"
    password = "admin_pass"
    if is_admin(id, password):
        return "ADMIN"
    else:
        return "LOGIN"

@app.route("^/login2$", "GET")
def login2(request):
    if is_admin(request):
        return "ADMIN"
    else:
        return "LOGIN"

#@app.route("^/home$", "GET")
def home(request):
    return "ADMIN"

home = app.route("^/home$", "GET")(home)

if __name__=="__main__":
    app.run(port=8000)
