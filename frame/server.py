from app import *

@app.route("^/$", "GET")
def index(request):
    return """
<form action="http://localhost:8000/login" method="post">
<input type="textarea" name="id" value="">
<input type="textarea" name="password" value="">
<input type="submit" value="送信">
</form>
    """

@app.route("^/login$", "POST")
def login(request):
    id = str(request.forms.get("id")[0])
    password = str(request.forms.get("password")[0])
    if is_admin(id, password):
        return "ADMIN_PAGE"
    else:
        return """
<form action="http://localhost:8000/login" method="post">
<input type="textarea" name="id" value="">
<input type="textarea" name="password" value="">
<input type="submit" value="送信">
</form>
        """

@app.route("^/login$", "GET")
def do_login(request):
    id = "admin"
    password = "admin_pass"
    if is_admin(id, password):
        return "ADMIN"
    else:
        return """
<form action="http://localhost:8000/login" method="post">
<input type="textarea" name="id" value="">
<input type="textarea" name="password" value="">
<input type="submit" value="送信">
</form>
        """

@app.route("^/login2$", "GET")
def login2(request):
    if is_admin(request):
        return "ADMIN"
    else:
        return """
<form action="http://localhost:8000/login" method="post">
<input type="textarea" name="id" value="">
<input type="textarea" name="password" value="">
<input type="submit" value="送信">
</form>
        """

#@app.route("^/home$", "GET")
def home(request):
    return "ADMIN"

home = app.route("^/home$", "GET")(home)

if __name__=="__main__":
    app.run(port=8000)
