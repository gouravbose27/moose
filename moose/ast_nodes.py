from lark import ast_utils
from typing import List
from dataclasses import dataclass,field
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

@dataclass
class FunctionDefinition(_Statement):
    name: str
    args: List[str] = field(default_factory=list)
    body: List[_Statement] = field(default_factory=list)

    def __init__(self, name: str, args=None, *body):
        self.name = name
        self.args = list(args) if args else []
        self.body = list(body)



@dataclass
class CallStatement(_Statement):

    name: str
    args: List[_Expression] = None

@dataclass
class ReturnStatement(_Statement):
    value: _Expression

@dataclass
class BinaryOperation(_Expression):
    left: _Expression
    op: str
    right: _Expression

@dataclass
class ComparisonOperation(_Expression):
    left: _Expression
    op: str
    right: _Expression


@dataclass
class WhileLoopStatement(_Statement):
    condition: _Expression
    body: List[_Statement]

@dataclass
class BreakStatement(_Statement):
    pass