import redis

def escape_special_query(query):
    # shuusei
    print("hoge")
    return query

def reverse_print(s):
    if isinstance(s, str):
        print(s[::-1])
    else:
        print("Not Str")
        print(s)

def is_admin(request):
    print("test is_admin")
    return True
