from abc import ABC, abstractmethod
import os
import sys

if __package__ in (None, ""):
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

from token.token import Token


class Node(ABC):
    @abstractmethod
    def tokenLiteral(self):
        pass


class Statement(Node):
    @abstractmethod
    def statementNode(self):
        pass


class Expression(Node):
    @abstractmethod
    def expressionNode(self):
        pass


class Program(Node):
    def __init__(self):
        self.statements = []

    def tokenLiteral(self):
        if len(self.statements) > 0:
            return self.statements[0].tokenLiteral()
        else:
            return ""


class Identifier(Expression):
    def __init__(self, token: Token, value):
        self.token = token
        self.value = value

    def expressionNode(self):
        pass

    def tokenLiteral(self):
        return self.token.literal


class LetStatement(Statement):
    def __init__(self, token: Token, name: Identifier, value: Expression):
        self.token = token
        self.name = name
        self.value = value

    def statementNode(self):
        pass

    def tokenLiteral(self):
        return self.token.literal
