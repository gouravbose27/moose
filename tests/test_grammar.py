# Parse small snippets with the raw Lark parser and assert terminal/rule shapes (comments, operators).
import pytest

from moose import parser
from moose.errors import MooseSyntaxError


def _stmt(tree, index=0):
    """Return the index-th top-level statement Tree of a parsed block."""
    return tree.children[index]


class TestPositiveCases:
    def test_arithmetic_precedence(self):
        tree = parser.parse("let x = 1 + 2 * 3\n")
        assignment = _stmt(tree)
        assert assignment.data == "assignment"
        add = assignment.children[1]
        assert add.data == "add"
        assert add.children[1].data == "mul"

    def test_if_else_blocks(self):
        tree = parser.parse("if x < 5:\nlet y = 1\nelse:\nlet y = 2\nend\n")
        if_stmt = _stmt(tree)
        assert if_stmt.data == "if_stmt"
        condition, then_block, else_block = if_stmt.children
        assert condition.data == "lt"
        assert then_block.data == "block" and len(then_block.children) == 1
        assert else_block.data == "block" and len(else_block.children) == 1

    def test_func_def_and_call(self):
        tree = parser.parse("def add(a, b):\nreturn a + b\nend\nlet z = add(1, 2)\n")
        func_def, assignment = tree.children
        assert func_def.data == "func_def"
        name, params, body = func_def.children
        assert name == "add"
        assert params.data == "params" and len(params.children) == 2
        assert body.data == "block"
        call = assignment.children[1]
        assert call.data == "call"
        arguments = call.children[1]
        assert arguments.data == "arguments" and len(arguments.children) == 2

    def test_boolean_operator_chain_precedence(self):
        tree = parser.parse("let ok = not a and b or c\n")
        or_ = _stmt(tree).children[1]
        assert or_.data == "or_"
        and_ = or_.children[0]
        assert and_.data == "and_"
        assert and_.children[0].data == "not_"

    def test_zero_arg_call(self):
        tree = parser.parse("let r = noop()\n")
        call = _stmt(tree).children[1]
        assert call.data == "call"
        arguments = call.children[1]
        assert arguments.data == "arguments" and len(arguments.children) == 0


class TestKeywordVsIdentifier:
    def test_identifiers_containing_keywords_are_not_split(self):
        tree = parser.parse("let lettuce = 1\nlet ifx = 2\nlet endpoint = 3\n")
        names = [stmt.children[0] for stmt in tree.children]
        assert names == ["lettuce", "ifx", "endpoint"]


class TestComments:
    def test_comment_only_line_and_trailing_comment_are_ignored(self):
        tree = parser.parse("# just a comment\nlet x = 1  # trailing comment\n")
        assert len(tree.children) == 1
        assert tree.children[0].data == "assignment"


class TestNegativeCases:
    def test_unterminated_if_raises_moose_syntax_error(self):
        with pytest.raises(MooseSyntaxError) as exc_info:
            parser.parse_program("if x < 5:\nlet y = 1\n")
        assert exc_info.value.line == 2

    def test_unexpected_character_raises_moose_syntax_error(self):
        with pytest.raises(MooseSyntaxError) as exc_info:
            parser.parse_program("let x = 1 @ 2\n")
        assert exc_info.value.line == 1

    def test_else_without_if_raises_moose_syntax_error(self):
        with pytest.raises(MooseSyntaxError) as exc_info:
            parser.parse_program("else:\nlet y = 2\nend\n")
        assert exc_info.value.line == 1
