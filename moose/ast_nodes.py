from lark import ast_utils
from typing import List
from dataclasses import dataclass
from lark.tree import Meta


# Transform the parse tree into a more usable format (Abstract Syntax Tree)


class _AST(ast_utils.Ast):
    # Base class for all AST nodes
    pass 

class _Statement(_AST):
    # Base class for all statement nodes
    pass

class _Expression(_AST):
    # Base class for all expression nodes
    pass

# AST node for a block of code containing multiple statements
@dataclass
class CodeBlock(_AST, ast_utils.AsList):
    statements: List[_Statement]

# AST node for a variable name
@dataclass
class Name(_Expression):
    name: str 

# AST node for a literal number
@dataclass
class Number(_Expression, ast_utils.WithMeta):
    meta: Meta
    value: int

# AST node for a literal string
@dataclass
class String(_Expression, ast_utils.WithMeta):
    meta: Meta
    value: str

# AST Node for a let statement
@dataclass
class LetStatement(_Statement):

    name: str
    value: _Expression

# AST Node for a boolean literal
@dataclass
class Boolean(_Expression, ast_utils.WithMeta):
    meta: Meta
    value: bool


# AST Node for print statement
@dataclass
class DisplayStatement(_Statement):
    value: _Expression

@dataclass
class IfStatement(_Statement):

    condition: _Expression
    body: List[_Statement]
    orelse: List[_Statement] = None


