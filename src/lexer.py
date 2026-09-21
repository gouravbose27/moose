'''
Lexer for the Moose project
Handles tokenization of source code

'''
from .token import *

class Lexer:
    def __init__(self, input: str):
        self.input = input # The source code to be tokenized
        self.position = 0 # Current position in the source code (points to the current char)
        self.read_position = 0 # Next position to read in the source code
        self.ch = None # Current character under examination
        self._read_char() # Initialize the first character

    def _read_char(self):
        if self.read_position >= len(self.input):
            self.ch = None
        else:
            self.ch = self.input[self.read_position]
        self.position = self.read_position
        self.read_position += 1

def new_token(token_type: str, literal: str) -> Token:
    token = Token()
    token.type = token_type
    token.literal = literal
    return token

def is_letter(ch: str) -> bool:
    return ch.isalpha() or ch == '_'


def read_identifier(lexer: Lexer) -> str:
    position = lexer.position
    while True:
        if not is_letter(lexer.ch):
            break

        lexer._read_char()

    return lexer.input[position:lexer.position]




def next_token(lexer: Lexer) -> Token:

    if is_letter(lexer.ch):
        literal = read_identifier(lexer)
        if literal in KEYWORDS:
            return new_token(KEYWORDS[literal], literal)
        else:
            return new_token(TokenType.IDENT, literal)


    if lexer.ch == '=':
        token = new_token(TokenType.ASSIGN, lexer.ch)
    elif lexer.ch == '+':
        token = new_token(TokenType.PLUS, lexer.ch)
    elif lexer.ch == '(':
        token = new_token(TokenType.LPAREN, lexer.ch)
    elif lexer.ch == ')':
        token = new_token(TokenType.RPAREN, lexer.ch)
    elif lexer.ch == '{':
        token = new_token(TokenType.LBRACE, lexer.ch)
    elif lexer.ch == '}':
        token = new_token(TokenType.RBRACE, lexer.ch)
    elif lexer.ch == ',':
        token = new_token(TokenType.COMMA, lexer.ch)
    elif lexer.ch == ';':
        token = new_token(TokenType.SEMICOLON, lexer.ch)
    elif lexer.ch is None:
        token = new_token(TokenType.EOF, "")
    else:
        token = new_token(TokenType.ILLEGAL, lexer.ch)

    lexer._read_char()
    return token

def is_letter(ch: str) -> bool:
    return ch.isalpha() or ch == '_'

def new_lexer(input: str) -> Lexer:
    return Lexer(input)



