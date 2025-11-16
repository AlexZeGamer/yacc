from yacc.codegen import CodeGenerator
from yacc.node import Node, NodeType
from yacc.lexer import Lexer
from yacc.parser import Parser
from yacc.sema import SemanticAnalyzer
from yacc.optimizer import Optimizer
from yacc.source import Source


def gen_stdout_for_node(node, capsys, locals_count: int = 0):
    cg = CodeGenerator(to_stdout=True)
    cg._start()
    func = Node(
        NodeType.NODE_FUNCTION,
        repr="main",
        value=locals_count,
        children=[Node(NodeType.NODE_BLOCK, children=[node])],
    )
    cg.codegen(func)
    asm = cg._finalize()
    cg._output(asm)
    out = capsys.readouterr().out
    return out


def test_codegen_constant_stdout(capsys):
    node = Node(NodeType.NODE_DEBUG, children=[Node(NodeType.NODE_CONST, value=5, children=[])])
    out = gen_stdout_for_node(node, capsys)
    assert out == ".start\nprep main\ncall 0\nhalt\n.main\npush 5\ndbg\npush 0\nret\n"


def test_codegen_unary_not_stdout(capsys):
    node = Node(NodeType.NODE_DEBUG, children=[Node(NodeType.NODE_NOT, children=[Node(NodeType.NODE_CONST, value=0, children=[])])])
    out = gen_stdout_for_node(node, capsys)
    assert out == ".start\nprep main\ncall 0\nhalt\n.main\npush 0\nnot\ndbg\npush 0\nret\n"


def test_codegen_unary_neg_stdout(capsys):
    node = Node(NodeType.NODE_DEBUG, children=[Node(NodeType.NODE_NEG, children=[Node(NodeType.NODE_CONST, value=2, children=[])])])
    out = gen_stdout_for_node(node, capsys)
    assert out == ".start\nprep main\ncall 0\nhalt\n.main\npush 0\npush 2\nsub\ndbg\npush 0\nret\n"


def test_codegen_pipeline_step_with_parser_sema_optimizer(capsys):
    src = Source.from_string("int main() { debug !1; }")
    parser = Parser(Lexer(src))
    sema = SemanticAnalyzer()
    opt = Optimizer()
    cg = CodeGenerator(to_stdout=True)

    cg._start()
    node = parser.parse()
    analyzed = sema.analyze(node)
    optimized = opt.optimize_ast(analyzed)
    cg.codegen(optimized, nbVars=sema.symbol_table.nbVars)
    asm = cg._finalize()
    cg._output(asm)

    out = capsys.readouterr().out
    assert out == ".start\nprep main\ncall 0\nhalt\n.main\npush 0\ndbg\npush 0\nret\n"


def test_codegen_if_without_else(capsys):
    node = Node(
        NodeType.NODE_COND,
        children=[
            Node(NodeType.NODE_CONST, value=1, children=[]),
            Node(
                NodeType.NODE_DEBUG,
                children=[Node(NodeType.NODE_CONST, value=2, children=[])],
            ),
        ],
    )
    out = gen_stdout_for_node(node, capsys)
    assert out == ".start\nprep main\ncall 0\nhalt\n.main\npush 1\njumpf L0_else\npush 2\ndbg\n.L0_else\npush 0\nret\n"


def test_codegen_if_with_else(capsys):
    node = Node(
        NodeType.NODE_COND,
        children=[
            Node(NodeType.NODE_CONST, value=1, children=[]),
            Node(
                NodeType.NODE_DEBUG,
                children=[Node(NodeType.NODE_CONST, value=2, children=[])],
            ),
            Node(
                NodeType.NODE_DEBUG,
                children=[Node(NodeType.NODE_CONST, value=3, children=[])],
            ),
        ],
    )
    out = gen_stdout_for_node(node, capsys)
    assert out == ".start\nprep main\ncall 0\nhalt\n.main\npush 1\njumpf L0_else\npush 2\ndbg\njump L0_end\n.L0_else\npush 3\ndbg\n.L0_end\npush 0\nret\n"


def test_codegen_simple_while_loop(capsys):
    loop = Node(
        NodeType.NODE_LOOP,
        children=[
            Node(NodeType.NODE_TARGET, value=False),
            Node(
                NodeType.NODE_COND,
                children=[
                    Node(NodeType.NODE_CONST, value=1, children=[]),
                    Node(
                        NodeType.NODE_DEBUG,
                        children=[Node(NodeType.NODE_CONST, value=1, children=[])],
                    ),
                    Node(NodeType.NODE_BREAK),
                ],
            ),
        ],
    )

    out = gen_stdout_for_node(loop, capsys)
    assert out == (
            ".start\n"
            "prep main\n"
            "call 0\n"
            "halt\n"
            ".main\n"
            ".L0_loop_start\n"
            "push 1\n"
            "jumpf L1_else\n"
            "push 1\n"
            "dbg\n"
            "jump L1_end\n"
            ".L1_else\n"
            "jump L0_loop_end\n"
            ".L1_end\n"
            "jump L0_loop_start\n"
            ".L0_loop_end\n"
            "push 0\n"
            "ret\n"
        )


def test_codegen_continue_uses_custom_target(capsys):
    loop = Node(
        NodeType.NODE_LOOP,
        children=[
            Node(
                NodeType.NODE_COND,
                children=[
                    Node(NodeType.NODE_CONST, value=1, children=[]),
                    Node(
                        NodeType.NODE_SEQ,
                        children=[
                            Node(NodeType.NODE_CONTINUE),
                            Node(NodeType.NODE_TARGET, value=True),
                            Node(
                                NodeType.NODE_DROP,
                                children=[Node(NodeType.NODE_CONST, value=2, children=[])],
                            ),
                        ],
                    ),
                    Node(NodeType.NODE_BREAK),
                ],
            ),
        ],
    )

    out = gen_stdout_for_node(loop, capsys)
    assert out == (
            ".start\n"
            "prep main\n"
            "call 0\n"
            "halt\n"
            ".main\n"
            ".L0_loop_start\n"
            "push 1\n"
            "jumpf L1_else\n"
            "jump L0_loop_continue\n"
            ".L0_loop_continue\n"
            "push 2\n"
            "drop 1\n"
            "jump L1_end\n"
            ".L1_else\n"
            "jump L0_loop_end\n"
            ".L1_end\n"
            "jump L0_loop_start\n"
            ".L0_loop_end\n"
            "push 0\n"
            "ret\n"
        )


def test_codegen_pointer_assignment_stdout(capsys):
    ptr_ref = Node(NodeType.NODE_REF, repr="ptr", index=0)
    deref = Node(NodeType.NODE_DEREF, children=[ptr_ref])
    assign = Node(
        NodeType.NODE_DROP,
        children=[Node(NodeType.NODE_AFFECT, children=[deref, Node(NodeType.NODE_CONST, value=7, children=[])])],
    )
    out = gen_stdout_for_node(assign, capsys, locals_count=1)
    assert out == (
        ".start\n"
        "prep main\n"
        "call 0\n"
        "halt\n"
        ".main\n"
        "resn 1\n"
        "push 7\n"
        "dup\n"
        "get 0\n"
        "write\n"
        "drop 1\n"
        "push 0\n"
        "ret\n"
    )


def test_codegen_pointer_read_stdout(capsys):
    ptr_ref = Node(NodeType.NODE_REF, repr="ptr", index=0)
    debug = Node(NodeType.NODE_DEBUG, children=[Node(NodeType.NODE_DEREF, children=[ptr_ref])])
    out = gen_stdout_for_node(debug, capsys, locals_count=1)
    assert out == (
        ".start\n"
        "prep main\n"
        "call 0\n"
        "halt\n"
        ".main\n"
        "resn 1\n"
        "get 0\n"
        "read\n"
        "dbg\n"
        "push 0\n"
        "ret\n"
    )


def test_codegen_address_of_local_stdout(capsys):
    var_ref = Node(NodeType.NODE_REF, repr="var", index=0)
    debug = Node(NodeType.NODE_DEBUG, children=[Node(NodeType.NODE_ADDRESS, children=[var_ref])])
    out = gen_stdout_for_node(debug, capsys, locals_count=1)
    assert out == (
        ".start\n"
        "prep main\n"
        "call 0\n"
        "halt\n"
        ".main\n"
        "resn 1\n"
        "prep start\n"
        "swap\n"
        "drop 1\n"
        "push 1\n"
        "sub\n"
        "push 0\n"
        "sub\n"
        "dbg\n"
        "push 0\n"
        "ret\n"
    )


def test_codegen_add_emits_add_instruction(capsys):
    expr = Node(
        NodeType.NODE_ADD,
        children=[Node(NodeType.NODE_CONST, value=1), Node(NodeType.NODE_CONST, value=2)],
    )
    node = Node(NodeType.NODE_DEBUG, children=[expr])
    out = gen_stdout_for_node(node, capsys)
    assert out == ".start\nprep main\ncall 0\nhalt\n.main\npush 1\npush 2\nadd\ndbg\npush 0\nret\n"


def test_codegen_cmp_eq_emits_cmpeq(capsys):
    expr = Node(
        NodeType.NODE_EQ,
        children=[Node(NodeType.NODE_CONST, value=3), Node(NodeType.NODE_CONST, value=4)],
    )
    node = Node(NodeType.NODE_DEBUG, children=[expr])
    out = gen_stdout_for_node(node, capsys)
    assert out == ".start\nprep main\ncall 0\nhalt\n.main\npush 3\npush 4\ncmpeq\ndbg\npush 0\nret\n"

