import re

# queryを修正する関数（dropとかなくす）
def escape_special_query(query):
    print("hoge")
    drop_patturn = r"drop"
    select_patturn = r"select"
    no_where_patturn = r"select.'+;.*--.+where"
    if re.match(drop_patturn, query):
        print("Drop Patturn Detected")
        return ""
    if re.match(select_patturn, query):
        if re.search(no_where_patturn, query):
            print("No Where Clause Patturn Detected")
            return ""
    return query

def reverse_print(s, *args, **kwargs):
    if isinstance(s, str):
        print(s[::-1], *args, **kwargs)
    else:
        print("Not Str")
        print(s, *args, **kwargs)

# is_adminを正しく動かす
# is_adminはlogin試行が正しくできているかの話？
# set_cookieはまたあとで、今回はidとpasswordを毎回調べる
def is_admin(id=None, password=None):
    if id is None or password is None:
        print("Login Required")
        return False
    if id == "admin" and password == "admin_pass":
        return True
    return False

#
def escape_xss_characters(s):
    if isinstance(s, str):
        return "Escape is over :)"
    else:
        return s