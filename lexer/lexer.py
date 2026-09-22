'''
Lexer for the Moose project
Handles tokenization of source code

'''

from token.token import *

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



# Create a new token instance
def new_token(token_type: str, literal: str) -> Token:
    token = Token()
    token.type = token_type
    token.literal = literal
    return token


# Read an identifier from the lexer
def read_identifier(lexer: Lexer) -> str:
    position = lexer.position
    while True:
        if not is_letter(lexer.ch):
            break

        lexer._read_char()

    return lexer.input[position:lexer.position]



# Get the next token from the lexer
def next_token(lexer: Lexer) -> Token:

    skip_whitespace(lexer)

    if lexer.ch is None:
        token = new_token(TokenType.EOF, "")
    elif lexer.ch == '=':
        if peek_char(lexer) == '=':
            lexer._read_char()
            token = new_token(TokenType.EQ, "==")
        else:
            token = new_token(TokenType.ASSIGN, lexer.ch)
    elif lexer.ch == '+':
        token = new_token(TokenType.PLUS, lexer.ch)
    elif lexer.ch == '-':
        token = new_token(TokenType.MINUS, lexer.ch)
    elif lexer.ch == '!':
        if peek_char(lexer) == '=':
            lexer._read_char()
            token = new_token(TokenType.NOT_EQ, "!=")
        else:
            token = new_token(TokenType.BANG, lexer.ch)

    elif lexer.ch == '/':
        token = new_token(TokenType.SLASH, lexer.ch)
    elif lexer.ch == '*':
        token = new_token(TokenType.ASTERISK, lexer.ch)
    elif lexer.ch == '<':
        token = new_token(TokenType.LT, lexer.ch)
    elif lexer.ch == '>':
        token = new_token(TokenType.GT, lexer.ch)
    elif lexer.ch == ',':
        token = new_token(TokenType.COMMA, lexer.ch)
    elif lexer.ch == ':':
        token = new_token(TokenType.COLON, lexer.ch)
    elif lexer.ch == '(':
        token = new_token(TokenType.LPAREN, lexer.ch)
    elif lexer.ch == ')':
        token = new_token(TokenType.RPAREN, lexer.ch)
    elif lexer.ch == '{':
        token = new_token(TokenType.LBRACE, lexer.ch)
    elif lexer.ch == '}':
        token = new_token(TokenType.RBRACE, lexer.ch)
    else:
        if is_letter(lexer.ch):
            literal = read_identifier(lexer)
            if literal in KEYWORDS:
                return new_token(KEYWORDS[literal], literal)
            else:
                return new_token(TokenType.IDENT, literal)
        elif is_number(lexer.ch):
            literal = read_number(lexer)
            return new_token(TokenType.INT, literal)
        else:
            token = new_token(TokenType.ILLEGAL, lexer.ch)

    lexer._read_char()
    return token

# Check if the character is a letter or underscore
def is_letter(ch: str | None) -> bool:
    return ch is not None and (ch.isalpha() or ch == '_')


# Check if the character is a number
def is_number(ch: str | None) -> bool:
    return ch is not None and ch.isdigit()

# Create a new lexer instance with the given input
def new_lexer(input: str) -> Lexer:
    return Lexer(input)

# Skip over any whitespace characters in the lexer input
def skip_whitespace(lexer: Lexer):
    while lexer.ch is not None and lexer.ch.isspace():
        lexer._read_char()

# Read a number from the lexer input
def read_number(lexer: Lexer) -> str:
    position = lexer.position
    while is_number(lexer.ch):
        lexer._read_char()
    return lexer.input[position:lexer.position]

def peek_char(lexer: Lexer) -> str:
    if lexer.read_position >= len(lexer.input):
        return None
    else:
        return lexer.input[lexer.read_position]