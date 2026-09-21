'''
Token definitions for the Moose project
Represents the types and structure of tokens used in the lexer

'''

class TokenType:

    # Special tokens
    ILLEGAL = 'ILLEGAL'
    EOF = 'EOF'

    # Identifiers + literals
    IDENT = 'IDENT'
    INT = 'INT'

    # Operators
    ASSIGN = '='
    PLUS = '+'

    # Delimiters
    COMMA = ','
    SEMICOLON = ';'
    COLON = ':'
    LPAREN = '('
    RPAREN = ')'
    LBRACE = '{'
    RBRACE = '}'

    # Keywords
    FUNCTION = 'FUNCTION'
    LET = 'LET'
    DEF = 'DEF'
    RETURN = 'RETURN'

class Token:
    def __init__(self, type = None | TokenType, literal =  None | str):
        self.type = type
        self.literal = literal

    def __repr__(self):
        return f"Token({self.type}, {self.literal})"



KEYWORDS = {
    "let": TokenType.LET,
    "def": TokenType.DEF,
    "return": TokenType.RETURN,
}

