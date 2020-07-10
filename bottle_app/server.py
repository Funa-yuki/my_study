from bottle import route, jinja2_template as template, request, run

@route('/', "GET")
def form():
    return template("index.html")

@route('/', "POST")
def post_index():
    form = request.forms.get('content')
    print(form)
    return template("index.html")

if __name__=="__main__":
    run(host='localhost', port='8888')
