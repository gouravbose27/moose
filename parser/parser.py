import os
import sys

if __package__ in (None, ""):
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

from ast.ast import *
from lexer.lexer import *
from token.token import *

class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.current_token = next_token(lexer)
        self.peek_token = next_token(lexer)

    def next_token(self):
        self.current_token = self.peek_token
        self.peek_token = next_token(self.lexer)
        return self.current_token

    