from lark import Lark


def get_parser(grammar : str, parser_type: str = 'lalr', maybe_placeholders: bool = True):
    # Create and return a Lark parser instance using the specified grammar
    # Initialize the parser with the grammar and LALR parser algorithm
    return Lark(grammar=grammar, parser=parser_type, maybe_placeholders=maybe_placeholders)