from parser import *
from ast_builder import ast_from_source
from py_transpiler import transpile
import pathlib


script_dir = pathlib.Path(__file__).parent

with open(script_dir / "grammar.lark", "r") as grammar_file:
    grammar = grammar_file.read()



parser = get_parser(grammar)

def repl():
    while True:
        # allow multi-line input
        source_code = ""
        while True:
            line = input(">> ")
            if line.strip() == "":
                break
            source_code += line + "\n"
            
        if source_code.strip() == "":
            continue
        ast = ast_from_source(source_code, parser)
        transpiled_code = transpile(ast)
        exec(transpiled_code)




