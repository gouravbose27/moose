# Loads grammar.lark into a Lark parser and exposes parse(source) -> AST (via ast_builder).

from lark import Lark
from lark.exceptions import UnexpectedInput
import pathlib
from ast_builder import ASTBuilder
from errors import MooseSyntaxError

parent_dir = pathlib.Path(__file__).parent

with open(parent_dir / "grammar.lark") as f:
    grammar = f.read()

parser = Lark(grammar, parser="lalr", propagate_positions=True)

def parse(source: str):
    return parser.parse(source)

#  higher-level parse_program(source: str) -> Program that runs the tree through ast_builder.AstBuilder().transform(tree). Catch lark.exceptions.UnexpectedInput and re-raise as MooseSyntaxError using e.line/e.column and e.get_context(source) for the message.


def parse_program(source: str):
    try:
        tree = parse(source)
        return ASTBuilder().transform(tree)
    except UnexpectedInput as e:
        raise MooseSyntaxError(f"Syntax error at line {e.line}, column {e.column}:\n{e.get_context(source)}") from e

print(parse("let x = 5").pretty())