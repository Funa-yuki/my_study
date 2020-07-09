
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

# is_adminを正しく動かす
# is_adminはlogin試行が正しくできているかの話？
# set_cookieはまたあとで、今回はidとpasswordを毎回調べる
def is_admin(id=None, password=None):
    if id is None or password is None:
        return False

    if id is "admin" and password is "admin_pass":
        return True
    return False
