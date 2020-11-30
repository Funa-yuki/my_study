import re
def ast_miyasuku(dumped_node: str) -> str:
    not_indent_l = []
    tab_l = []
    kaigyo_l = []
    tab_count = 0
    l = re.split("(?<=[\(\),\[\]])", dumped_node)

    for elem in l:
        if elem and elem[0] == " ":
            elem = elem[1:]
        not_indent_l.append(elem)

    for elem in not_indent_l:
        tab_l.append(str(tab_count) + " " + tab_count * "  " + elem)
        if elem and (elem[-1] is "(" or elem[-1] is "["):
            tab_count += 1
        elif elem and (elem[-1] is ")" or elem[-1] is "]"):
            tab_count -= 1
    for elem in tab_l:
        kaigyo_l.append(elem + "\n")

    new_str = "".join(kaigyo_l)
    return new_str


if __name__=="__main__":
    #s = "Call(a, b, c)"
    #print(s[4])
    #print(s[4:])
    #print(s[:4])
    #"Return(value=Call(func=Attribute(value=Name(id='html', ctx=Load()), attr='format', ctx=Load()), args=[Call(func=Name(id='escape_xss_characters', ctx=Load()), args=[Str(s='sobasoba')], keywords=[])], keywords=[]))"
    print(ast_miyasuku("Return(value=Call(func=Attribute(value=Name(id='html', ctx=Load()), attr='format', ctx=Load()), args=[Call(func=Name(id='escape_xss_characters', ctx=Load()), args=[Str(s='sobasoba')], keywords=[])], keywords=[]))"))
