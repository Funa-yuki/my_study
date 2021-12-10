def decorator(func):
    def wrapper(*args, **kwargs):
        print('--func の前の処理--')
        func(*args, **kwargs)
        print('--func の後の処理--')
    return wrapper

@ decorator
def function(x, y):
    
'''
'''

def decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print('decorate')
        s = args[0]
        for e in s:
            if e == '*':
                print('escape')
                break
        func(*args, **kwargs)
    return wrapper

@decorator
def execute(query):
    super(sqlite3.Connection, self).execute(query)

'''
'''

class sqlite3(sqlite3):
    class Cursor(Cursor):
        def execute(query):
        print('override')
        for e in query:
            if e == '*':
                print('escape')
                break
        super().execute(query)

'''
'''
class Cursor(sqlite3.Cursor):
    def execute(query):
        print('override')
        for e in query:
            if e == '*':
                print('escape')
                break
        super().execute(query)
sqlite3.Cursor = Cursor

'''
'''


'''
'''


'''
'''


'''
'''


