# Loads grammar.lark into a Lark parser and exposes parse(source) -> AST (via ast_builder).

from lark import Lark, Tree
from lark.exceptions import UnexpectedInput
import pathlib
from . import ast_builder
from . import errors

parent_dir = pathlib.Path(__file__).parent

with open(parent_dir / "grammar.lark") as f:
    grammar = f.read()

parser = Lark(grammar, parser="lalr", propagate_positions=True)

def parse(source: str) -> Tree:
    return parser.parse(source)



def parse_program(source: str):
    try:
        tree = parse(source)
        return ast_builder.ASTBuilder().transform(tree)
    except UnexpectedInput as e:
        msg = f"Unexpected input at line {e.line}: {e.get_context(source).strip()}"
        raise errors.MooseSyntaxError(message = msg, line = e.line) 

