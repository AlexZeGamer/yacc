from yacc.node import Node, NodeType
from yacc.optimizer import Optimizer


def test_optimizer_is_passthrough_identity():
    opt = Optimizer()
    node = Node(NodeType.NODE_CONST, value=9)
    assert opt.optimize_ast(node) is node


def test_optimizer_constant_folding_addition():
    opt = Optimizer()
    left = Node(NodeType.NODE_CONST, value=2)
    right = Node(NodeType.NODE_CONST, value=3)
    expr = Node(NodeType.NODE_ADD, children=[left, right])

    out = opt.optimize_ast(expr)

    assert out.type == NodeType.NODE_CONST
    assert out.value == 5
    assert out.children == []


def test_optimizer_dead_code_eliminates_constant_drop():
    opt = Optimizer()
    drop_child = Node(NodeType.NODE_CONST, value=0)
    drop = Node(NodeType.NODE_DROP, children=[drop_child])
    seq = Node(NodeType.NODE_SEQ, children=[drop])

    assert opt.optimize_ast(seq) is None


def test_optimizer_conditional_with_constant_condition():
    opt = Optimizer()
    cond = Node(NodeType.NODE_CONST, value=0)
    then_branch = Node(NodeType.NODE_DEBUG, children=[Node(NodeType.NODE_CONST, value=1)])
    else_branch = Node(NodeType.NODE_DROP, children=[Node(NodeType.NODE_CONST, value=7)])
    node = Node(NodeType.NODE_COND, children=[cond, then_branch, else_branch])

    assert opt.optimize_ast(node) is None


def test_optimizer_keeps_non_constant_drop():
    opt = Optimizer()
    drop_child = Node(NodeType.NODE_REF, repr="x")
    drop = Node(NodeType.NODE_DROP, children=[drop_child])

    out = opt.optimize_ast(drop)
    assert out is drop
    assert out.children[0] is drop_child


def test_optimizer_does_not_fold_division_by_zero():
    opt = Optimizer()
    left = Node(NodeType.NODE_CONST, value=10)
    right = Node(NodeType.NODE_CONST, value=0)
    div = Node(NodeType.NODE_DIV, children=[left, right])

    out = opt.optimize_ast(div)

    assert out.type == NodeType.NODE_DIV
    assert out.children[0].value == 10
    assert out.children[1].value == 0
