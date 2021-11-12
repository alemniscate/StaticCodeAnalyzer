import sys
import os
import re
import ast

message_dict = {
1:"Too long",
2:"Indentation is not a multiple of four",
3:"Unnecessary semicolon",
4:"At least two spaces required before inline comments",
5:"TODO found",
6:"More than two blank lines used before this line",
7:"Too many spaces after '%s'",
8:"Class name '%s' should use CamelCase",
9:"Function name '%s' should use snake_case",
10:"Argument name '%s' should be snake_case",
11:"Variable '%s' in function should be snake_case",
12:"Default argument value is mutable"
}

def analyze(filename):
    if not filename.endswith(".py"):
        return

    with open(filename) as f:
        lines = f.readlines()

    with open(filename) as f:
        text = f.read()
    tree = ast.parse(text)    

    error_set = set()
    for i, line in enumerate(lines):
        check_s001(i, line, error_set)
        check_s002(i, line, error_set)
        check_s003(i, line, error_set)
        check_s004(i, line, error_set)
        check_s005(i, line, error_set)
        check_s007(i, line, error_set)
        check_s008(i, line, error_set)
        check_s009(i, line, error_set)
    check_s006(lines, error_set)
    check_s010(tree, error_set)
    check_s011(tree, error_set)
    check_s012(tree, error_set)

    error_list = list(error_set)
    error_list.sort()
    for error in error_list:
        linenumber, code, name = error
        message = message_dict[code]
        message = message.replace("%s", name)
        print(f"{filename}: Line {linenumber}: S{code:03} {message}")

def check_s001(i, line, error_set):
    if len(line) > 79:
        error_set.add((i + 1, 1, ""))

def check_s002(i, line, error_set):
    if line == "\n":
        return
    indent = len(line) - len(line.lstrip())
    if indent % 4 != 0:
        error_set.add((i + 1, 2, ""))

def check_s003(i, line, error_set):
    semicolon_index = line.find(";")
    if semicolon_index == -1:
        return

    squtoe_start_index = line.find("'")
    squtoe_end_index = line.find("'", squtoe_start_index + 1)
    dqutoe_start_index = line.find('"')
    dqutoe_end_index = line.find('"', dqutoe_start_index + 1)

    if squtoe_start_index > -1:
        if squtoe_start_index < semicolon_index < squtoe_end_index:
            return

    if dqutoe_start_index > -1:
        if dqutoe_start_index < semicolon_index < dqutoe_end_index:
            return

    comment_index = line.find("#")
    if comment_index == -1:
        error_set.add((i + 1, 3, ""))
    if comment_index > semicolon_index:
        error_set.add((i + 1, 3, ""))

def check_s004(i, line, error_set):
    comment_index = line.find("#")
    if comment_index == -1:
        return
    if comment_index > 0 and line[comment_index - 1] != " ":
        error_set.add((i + 1, 4, ""))
    if comment_index > 1 and line[comment_index - 2] != " ":
        error_set.add((i + 1, 4, ""))

def check_s005(i, line, error_set):
    comment_index = line.find("#")
    if comment_index == -1:
        return

    if line.lower().find("todo") > comment_index:
        error_set.add((i + 1, 5, ""))

def check_s006(lines, error_set):
    for i, line in enumerate(lines): 
        if line == "\n":
            continue

        if i > 2:
            if lines[i - 1] == "\n" and lines[i - 2] == "\n" and lines[i - 3] == "\n":
                error_set.add((i + 1, 6, ""))

def check_s007(i, line, error_set):
    if re.match(" *def  .*", line):
        error_set.add((i + 1, 7, "def"))

    if re.match(" *class  .*", line):
        error_set.add((i + 1, 7, "class"))

def check_s008(i, line, error_set):
    if not line.startswith("class "):
        return

    name = line.strip(":\n").split()[1]
    elms = name.split("(")
    if len(elms) > 1:
        name = elms[0]
    if name[0].upper() != name[0]:
        error_set.add((i + 1, 8, name))

def is_snake_case(name):
    if name[0] == "_":
        return True
    if name[0].upper() == name[0]:
        return False

    m = re.search("\d", name)
    if m:
        d = m.group()
        index = name.index(d)
        if name[index - 1] != "_":
            return False

    return True

def check_s009(i, line, error_set):
    if not re.match("\s*def ", line):
        return

    name = line.strip(":\n").split()[1]
    elms = name.split("(")
    if len(elms) > 1:
        name = elms[0]
    if not is_snake_case(name):
        error_set.add((i + 1, 9, name))

def check_s010(tree, error_set):
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            args_list=node.args.args
            for arg in args_list:
                if not is_snake_case(arg.arg):
                    error_set.add((arg.lineno, 10, arg.arg))

def check_s011(tree, error_set):
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            variable_list = node.body
            for variable in variable_list:
                if isinstance(variable, ast.Assign):
                    for target in variable.targets:
                        if isinstance(target, ast.Name):
                            if not is_snake_case(target.id):
                                error_set.add((target.lineno, 11, target.id))

def check_s012(tree, error_set):
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            arg_list=node.args.args
            default_list=node.args.defaults
            for i, default in enumerate(default_list):
                if isinstance(default, ast.List):
                    error_set.add((default.lineno, 12, ""))

def get_arg():
    if len(sys.argv) == 1:
        return "test/this_stage"
#        return "test8.py"
    elif len(sys.argv) == 2:
        return sys.argv[1]
    else:
        return None 

if __name__ == "__main__":
    pathname = get_arg()
#    print(os.path.abspath(pathname))
    if os.path.isdir(pathname):
        for entry in os.scandir(pathname):
            if not entry.is_file():
                continue
            analyze(entry.path)
    if os.path.isfile(pathname):
        analyze(pathname)