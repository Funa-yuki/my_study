from app import *
from bottle import jinja2_template as tmpl

@app.route("^/$")
def index(request):
    return tmpl("index.html", name="hoge")

@app.route("^/access$")
def access(request):
    request.queries
    return tmpl("access.html", name="hoge")

if __name__=="__main__":
    app.run(port=8888)
