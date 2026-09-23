# This is the REPL for the Moose language

import os
import sys

if __package__ in (None, ""):
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

from lexer.lexer import new_lexer, next_token

def repl():
    while input_text := input(">> "):
        l = new_lexer(input=input_text)
        token = next_token(lexer=l)

        while token.type != "EOF":
            print(token)
            token = next_token(lexer=l)

