from lark import  Lark,Transformer, v_args, ast_utils
from ast_nodes import *
import sys

this_module = sys.modules[__name__]

@v_args(inline=True)
class ToAst(Transformer):
    
    def STRING(self, s):
    # Remove quotation marks
        return s[1:-1]

    def DEC_NUMBER(self, n):
        return int(n)
   
    def start(self, x):
        return x

    def boolean_true(self):
        return Boolean(meta=Meta(), value=True)

    def boolean_false(self):
        return Boolean(meta=Meta(), value=False)
    

    def statement(self, stmt):
        return stmt
    
    def if_statement(self, condition, body, orelse=None):
        return IfStatement(condition=condition, body=list(body), orelse=list(orelse) if orelse else None)




def ast_from_source(source_code, parser: Lark) -> ast_utils.Ast:
    transformer = ast_utils.create_transformer(this_module, ToAst())
    tree = parser.parse(source_code)
    return transformer.transform(tree)

