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
        self.current_token = None
        self.peek_token = next_token(self.lexer)

    def next_token(self):
        self.current_token = self.peek_token
        self.peek_token = next_token(self.lexer)


def new_parser(lexer: Lexer) -> Parser:
    parser = Parser(lexer=lexer)
    parser.next_token()
    return parser

def parse_program(parser: Parser) -> Program:
    # Implement the parsing logic for the program here
    
    return None

    