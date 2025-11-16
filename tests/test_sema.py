import pytest

from yacc.lexer import Lexer
from yacc.node import Node, NodeType
from yacc.parser import Parser
from yacc.sema import SemanticAnalyzer
from yacc.source import Source
from yacc.utils.errors import CompilationError


def analyze_text(source: str) -> Node | None:
    src = Source.from_string(source)
    parser = Parser(Lexer(src))
    node = parser.parse()
    sema = SemanticAnalyzer(source_code=src)
    return sema.analyze(node)


def test_sema_is_passthrough_identity():
    sema = SemanticAnalyzer()
    node = Node(NodeType.NODE_CONST, value=7)
    assert sema.analyze(node) is node


def test_sema_break_outside_loop_raises():
    sema = SemanticAnalyzer()
    node = Node(NodeType.NODE_BREAK)
    with pytest.raises(CompilationError):
        sema.analyze(node)


def test_sema_continue_outside_loop_raises():
    sema = SemanticAnalyzer()
    node = Node(NodeType.NODE_CONTINUE)
    with pytest.raises(CompilationError):
        sema.analyze(node)


def test_sema_break_inside_loop_allowed():
    loop = Node(
        NodeType.NODE_LOOP,
        children=[
            Node(
                NodeType.NODE_COND,
                children=[
                    Node(NodeType.NODE_CONST, value=1),
                    Node(NodeType.NODE_BREAK),
                ],
            )
        ],
    )
    sema = SemanticAnalyzer()
    assert sema.analyze(loop) is loop


def test_sema_function_with_return_is_valid():
    program = "int main() { int value; value = 1; return value; }"
    analyzed = analyze_text(program)
    assert analyzed.type == NodeType.NODE_FUNCTION
    body = analyzed.children[-1]
    assert any(child.type == NodeType.NODE_RETURN for child in body.children)


def test_sema_return_outside_function_raises():
    sema = SemanticAnalyzer()
    node = Node(NodeType.NODE_RETURN, children=[Node(NodeType.NODE_CONST, value=0)])
    with pytest.raises(CompilationError):
        sema.analyze(node)


def test_sema_duplicate_declaration_raises():
    block = Node(
        NodeType.NODE_BLOCK,
        children=[
            Node(NodeType.NODE_DECLARE, repr="x"),
            Node(NodeType.NODE_DECLARE, repr="x"),
        ],
    )
    sema = SemanticAnalyzer()
    with pytest.raises(CompilationError):
        sema.analyze(block)


def test_sema_detects_unknown_symbol():
    ref = Node(NodeType.NODE_REF, repr="unknown")
    sema = SemanticAnalyzer()
    with pytest.raises((CompilationError, ValueError)):
        sema.analyze(ref)
