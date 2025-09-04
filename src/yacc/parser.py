from .token import Token, TokenType
from .node import Node, NodeType
from .lexer import Lexer

class Parser:
    def __init__(self, lexer: Lexer = None):
        self.lexer = lexer or Lexer("")
        self.current_token: Token = lexer.T

    def parse(self) -> Node:
        """Entry point"""
        if self.lexer.T is None or self.lexer.T.type == TokenType.TOK_EOF:
            return None
        return self.I()

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

        # E ;  => drop
        N = self.E()
        self.lexer.accept(TokenType.TOK_SEMICOLON)
        return Node(NodeType.NODE_DROP, children=[N])
