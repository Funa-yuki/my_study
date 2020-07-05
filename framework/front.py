import re

def change_text_to_regular_explession(input):
    output = ""
    for c in input:
        if c is '.':
            output += "\."
        else:
            output += c
    return output

def escape(name, chr):
    if chr is None:
        return name

    patturn = change_text_to_regular_explession(chr)
    if re.search(patturn, name):
        print(re.sub(patturn, "", name))
        return re.sub(patturn, "", name)
    return name


# 今後filenameの正しいエスケープが必要
def template(filename):
    filename = escape(filename, chr="../")
    type(filename)
    filename = "templates/" + filename
    with open(filename,mode="r") as f:
        page = f.read()
    return page
