# This is the REPL for the Moose language

from lexer.lexer import new_lexer, next_token

def repl():
    while input_text := input(">> "):
        l = new_lexer(input=input_text)
        token = next_token(lexer=l)

        while token.type != "EOF":
            print(token)
            token = next_token(lexer=l)

