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
    MINUS = '-'
    BANG = '!'
    SLASH = '/'
    ASTERISK = '*'
    LT = '<'
    GT = '>'
    EQ = '=='
    NOT_EQ = '!='

    # Delimiters
    COMMA = ','
    COLON = ':'
    LPAREN = '('
    RPAREN = ')'
    LBRACE = '{'
    RBRACE = '}'

    # Keywords / Reserved words
    FUNCTION = 'FUNCTION'
    LET = 'LET'
    DEF = 'DEF'
    RETURN = 'RETURN'
    IF = 'IF'
    ELSE = 'ELSE'
    ELIF = 'ELIF'
    TRUE = 'TRUE'
    FALSE = 'FALSE'

class Token:
    def __init__(self, type = None | TokenType, literal =  None | str):
        self.type = type
        self.literal = literal

    def __repr__(self):
        return f"Token({self.type}, {self.literal})"


# Keywords / Reserved words
KEYWORDS = {
    "let": TokenType.LET,
    "def": TokenType.DEF,
    "return": TokenType.RETURN,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "elif": TokenType.ELIF,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE
    
}

