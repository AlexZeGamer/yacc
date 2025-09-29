from .token import Token, TokenType
from .node import Node, NodeType
from .source import Source

from .lexer import Lexer

from .utils.errors import CompilationError
from .utils.logger import Logger

class Parser:

    def __init__(self, lexer: Lexer, source_code: Source = None, verbose: bool = False):
        self.lexer = lexer or Lexer(source_code, verbose)
        self.source_code = source_code
        self.verbose = verbose

    def parse(self) -> Node:
        """Entry point"""
        if self.lexer.T is None or self.lexer.T.type == TokenType.TOK_EOF:
            return None
        
        N: Node = self.I()
        if self.verbose:
            Logger.log("Syntax analysis / Parsing (AST):")
            N.print(mode="beautify")
        
        return N

    # Grammar implementation
    def E(self, prio: int = 0) -> Node:
        """Parse binary operations expressions"""
        N = self.P()  # first argument

        # continue parsing binary operations as long as the next token is a binary operator with right priority
        while self.lexer.T and self.lexer.T.type in Node.OP:
            op_tok = self.lexer.T.type
            if Node.OP[op_tok]["prio"] < prio:
                break  # priority filter
            self.lexer.next()
            M = self.E(
                Node.OP[op_tok]["prio_arg"]
            )  # second argument (can be another expression)
            N = Node(Node.OP[op_tok]["ntype"], children=[N, M])

        return N

    def A(self) -> Node:
        """Parse atomic expressions"""
        # A -> nb | (E)
        # number
        if self.lexer.check(TokenType.TOK_CONST):
            # The value is on T_prev after advancing
            value = self.lexer.T_prev.value
            return Node(NodeType.NODE_CONST, value=value, children=[])

        # (E)
        if self.lexer.check(TokenType.TOK_LPARENTHESIS):
            r = self.E()
            # require )
            self.lexer.accept(TokenType.TOK_RPARENTHESIS)
            return r

        # <id>
        if self.lexer.check(TokenType.TOK_IDENT):
            return Node(NodeType.NODE_REF, repr=self.lexer.T_prev.repr)

        # error
        line, col = self.lexer.source_code.pos_to_line_col(self.lexer.pos)
        raise SyntaxError(
            f"Unexpected token {self.lexer.T.repr!r} at line {line}, column {col}: expected constant or '('"
        )

    def P(self) -> Node:
        """Parse expressions with unary prefix operators"""
        # P -> !P | -P | +P | S
        if self.lexer.check(TokenType.TOK_NOT):
            # [not]->[P]
            return Node(NodeType.NODE_NOT, children=[self.P()])
        elif self.lexer.check(TokenType.TOK_SUB):
            # [neg]->[P]
            return Node(NodeType.NODE_NEG, children=[self.P()])
        elif self.lexer.check(TokenType.TOK_ADD):
            # +P => P
            return self.P()
        # default: S
        return self.S()

    def S(self) -> Node:
        """Parse expressions with unary suffix operators"""
        # S -> A
        return self.A() # TODO: implement suffix operators (function calls, array indexing)

    def I(self) -> Node:
        """Parse an instruction ("expr;", block or debug)"""
        # debug E ;
        if self.lexer.check(TokenType.TOK_DEBUG):
            N = self.E()
            self.lexer.accept(TokenType.TOK_SEMICOLON)
            return Node(NodeType.NODE_DEBUG, children=[N])

        # { I* }
        if self.lexer.check(TokenType.TOK_LBRACE):
            block = Node(NodeType.NODE_BLOCK, children=[])
            while not self.lexer.check(TokenType.TOK_RBRACE):
                block.add_child(self.I())
            return block

        # int <id> ; (declaration)
        if self.lexer.check(TokenType.TOK_INT):
            N = Node(NodeType.NODE_DECLARE, repr=self.lexer.T.repr)
            self.lexer.accept(TokenType.TOK_IDENT)
            self.lexer.accept(TokenType.TOK_SEMICOLON)
            return N

        # E ;  => drop
        N = self.E()
        self.lexer.accept(TokenType.TOK_SEMICOLON)
        return Node(NodeType.NODE_DROP, children=[N])
