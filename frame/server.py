from app import *

@app.route("^/$", "GET")
def index(request):
    print("hoge")
    return "INDEX"

@app.route("^/login$", "GET")
def login(request):
    print(is_admin(request))
    return "LOGIN"

@app.route("^/login$", "POST")
def do_login(request):
    if is_admin(request):
        return "ADMIN"
    else:
        return "LOGIN"

@app.route("^/login2$", "GET")
def login2(request):
    if is_admin(request):
        return "ADMIN"
    else:
        return "LOGIN"

@app.route("^/home$", "GET")
def home(request):
    return "ADMIN"

if __name__=="__main__":
    app.run(port=8000)
