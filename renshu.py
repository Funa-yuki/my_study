



@app.addNodeFixer("rewriteExecuteRequestArgs")
def func1(request):

    import sqlite3
    conn = sqlite3.connect("test1.db")
    cur = conn.cursor()

    cur.execute("select * from table1 where ID = " + request.params.get("ID") + \
    " and Password = " + request.params.get("Password"))

    data = cur.fetchone()
    conn.commit()

    return "Return: Hello, " + data[1] + ". Your ID is " + data[0]
