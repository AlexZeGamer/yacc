import pytest

from yacc.lexer import Lexer
from yacc.node import NodeType
from yacc.parser import Parser
from yacc.source import Source
from yacc.utils.errors import CompilationError


def parse_function(text: str):
    return Parser(Lexer(Source.from_string(text))).parse()


def parse_instruction(text: str):
    program = f"int main() {{ {text} }}"
    node = parse_function(program)
    assert node.type == NodeType.NODE_FUNCTION
    body = node.children[-1]
    if body.type == NodeType.NODE_BLOCK and body.children:
        return body.children[0]
    return body


def test_parse_constant_as_instruction_drop():
    n = parse_instruction("123;")
    assert n.type == NodeType.NODE_DROP
    assert n.children[0].type == NodeType.NODE_CONST
    assert n.children[0].value == 123


def test_parse_parentheses_as_instruction_drop():
    n = parse_instruction("(1);")
    assert n.type == NodeType.NODE_DROP
    assert n.children[0].type == NodeType.NODE_CONST
    assert n.children[0].value == 1


def test_parse_unary_not_debug():
    n = parse_instruction("debug !1;")
    assert n.type == NodeType.NODE_DEBUG
    child = n.children[0]
    assert child.type == NodeType.NODE_NOT
    assert child.children[0].value == 1


def test_parse_unary_negative_debug():
    n = parse_instruction("debug -1;")
    assert n.type == NodeType.NODE_DEBUG
    inner = n.children[0]
    assert inner.type == NodeType.NODE_NEG
    assert inner.children[0].value == 1


def test_parse_unary_plus_is_noop_drop():
    n = parse_instruction("+1;")
    assert n.type == NodeType.NODE_DROP
    assert n.children[0].type == NodeType.NODE_CONST


def test_parse_identifier_reference():
    n = parse_instruction("abc;")
    assert n.type == NodeType.NODE_DROP
    assert n.children[0].type == NodeType.NODE_REF
    assert n.children[0].repr == "abc"


def test_parse_post_increment():
    n = parse_instruction("i++;")
    drop = n
    assert drop.type == NodeType.NODE_DROP
    affect = drop.children[0]
    assert affect.type == NodeType.NODE_AFFECT
    ref_lhs, rhs = affect.children
    assert ref_lhs.type == NodeType.NODE_REF and ref_lhs.repr == "i"
    assert rhs.type == NodeType.NODE_ADD
    assert rhs.children[0].repr == "i"
    assert rhs.children[1].value == 1


def test_parse_if_without_else():
    n = parse_instruction("if (1) debug 2;")
    assert n.type == NodeType.NODE_COND
    cond, then_branch = n.children
    assert cond.value == 1
    assert then_branch.type == NodeType.NODE_DEBUG


def test_parse_if_with_else():
    n = parse_instruction("if (1) debug 2; else debug 3;")
    assert n.type == NodeType.NODE_COND
    cond, then_branch, else_branch = n.children
    assert cond.value == 1
    assert then_branch.type == NodeType.NODE_DEBUG
    assert else_branch.type == NodeType.NODE_DEBUG


def test_parse_function_definition_with_parameters():
    fn = parse_function("int sum(int a, int b) { return a + b; }")
    assert fn.type == NodeType.NODE_FUNCTION
    assert fn.repr == "sum"
    params = fn.children[:-1]
    body = fn.children[-1]
    assert [param.repr for param in params] == ["a", "b"]
    assert body.type == NodeType.NODE_BLOCK
    assert body.children[0].type == NodeType.NODE_RETURN


def test_parse_return_statement():
    node = parse_instruction("return 42;")
    assert node.type == NodeType.NODE_RETURN
    assert node.children[0].value == 42


def test_parse_function_call_expression():
    drop = parse_instruction("foo(1, 2);")
    assert drop.type == NodeType.NODE_DROP
    call = drop.children[0]
    assert call.type == NodeType.NODE_CALL
    assert call.children[0].repr == "foo"
    args = call.children[1:]
    assert len(args) == 2
    assert [arg.value for arg in args] == [1, 2]


def test_parse_declaration_with_initializer():
    node = parse_instruction("int a = 5;")
    assert node.type == NodeType.NODE_SEQ
    decl, drop = node.children
    assert decl.type == NodeType.NODE_DECLARE and decl.repr == "a"
    assign = drop.children[0]
    lhs, rhs = assign.children
    assert lhs.type == NodeType.NODE_REF and rhs.value == 5


def test_parse_pointer_declaration_with_stars():
    decl = parse_instruction("int **ptr;")
    assert decl.type == NodeType.NODE_DECLARE
    assert decl.repr == "ptr"


def test_parse_pointer_indirection_expression():
    drop = parse_instruction("*ptr;")
    deref = drop.children[0]
    assert deref.type == NodeType.NODE_DEREF
    assert deref.children[0].repr == "ptr"


def test_parse_address_of_identifier_expression():
    drop = parse_instruction("&value;")
    addr = drop.children[0]
    assert addr.type == NodeType.NODE_ADDRESS
    assert addr.children[0].repr == "value"


def test_parse_array_index_expression():
    drop = parse_instruction("arr[i];")
    deref = drop.children[0]
    plus = deref.children[0]
    left, right = plus.children
    assert left.repr == "arr"
    assert right.repr == "i"


def test_parse_add_mul_precedence():
    n = parse_instruction("debug 1+2*3;")
    assert n.type == NodeType.NODE_DEBUG
    expr = n.children[0]
    assert expr.type == NodeType.NODE_ADD
    r = expr.children[1]
    assert r.type == NodeType.NODE_MUL


def test_parse_chain_left_associative():
    n = parse_instruction("debug 4-3-2;")
    expr = n.children[0]
    assert expr.type == NodeType.NODE_SUB
    left = expr.children[0]
    assert left.type == NodeType.NODE_SUB


def test_parse_while_loop():
    node = parse_instruction("while (1) debug 2;")
    assert node.type == NodeType.NODE_LOOP
    target, cond = node.children
    assert target.type == NodeType.NODE_TARGET and target.value is False
    assert cond.type == NodeType.NODE_COND
    assert cond.children[0].value == 1
    assert cond.children[1].type == NodeType.NODE_DEBUG
    assert cond.children[2].type == NodeType.NODE_BREAK


def test_parse_do_while_loop():
    node = parse_instruction("do debug 1; while (0);")
    body, target, cond = node.children
    assert body.type == NodeType.NODE_DEBUG
    assert target.type == NodeType.NODE_TARGET and target.value is True
    assert cond.children[0].type == NodeType.NODE_NOT
    assert cond.children[0].children[0].value == 0
    assert cond.children[1].type == NodeType.NODE_BREAK


def test_parse_for_loop_structure():
    node = parse_instruction("for (i; i; i) debug i;")
    assert node.type == NodeType.NODE_SEQ
    init, loop = node.children
    assert init.type == NodeType.NODE_DROP
    assert loop.type == NodeType.NODE_LOOP
    cond = loop.children[0]
    assert cond.type == NodeType.NODE_COND
    then_branch = cond.children[1]
    body, target, post = then_branch.children
    assert body.type == NodeType.NODE_DEBUG
    assert target.type == NodeType.NODE_TARGET and target.value is True
    assert post.type == NodeType.NODE_DROP


def test_parse_for_loop_with_declaration_and_step_inc():
    node = parse_instruction("for (int i = 0; i; i++) debug i;")
    init, loop = node.children
    decl, init_assign = init.children
    assert decl.type == NodeType.NODE_DECLARE and decl.repr == "i"
    assert init_assign.children[0].type == NodeType.NODE_AFFECT
    cond = loop.children[0]
    assert cond.children[0].type == NodeType.NODE_REF
    then_branch = cond.children[1]
    step_drop = then_branch.children[2]
    affect = step_drop.children[0]
    rhs = affect.children[1]
    assert rhs.type == NodeType.NODE_ADD
    assert rhs.children[1].value == 1


def test_parse_break_statement():
    node = parse_instruction("break;")
    assert node.type == NodeType.NODE_BREAK


def test_parse_continue_statement():
    node = parse_instruction("continue;")
    assert node.type == NodeType.NODE_CONTINUE


def test_parser_missing_semicolon_raises():
    src = "int main() { debug 1 }"
    parser = Parser(Lexer(Source.from_string(src)))
    with pytest.raises((SyntaxError, CompilationError)):
        parser.parse()


def test_parser_postfix_requires_identifier():
    src = "int main() { 1++; }"
    parser = Parser(Lexer(Source.from_string(src)))
    with pytest.raises(CompilationError):
        parser.parse()
