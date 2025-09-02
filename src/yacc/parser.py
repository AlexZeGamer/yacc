from .token import Token, TokenType
from .node import Node, NodeType
from .lexer import Lexer

class Parser:
    def __init__(self, lexer: Lexer = None):
        self.lexer = lexer or Lexer("")
        self.current_token: Token = lexer.T

    def parse(self) -> Node:
        """Entry point: E -> P"""
        if self.lexer.T is None or self.lexer.T.type == TokenType.TOK_EOF:
            return None
        return self.E()

    # Grammar implementation
    def E(self) -> Node:
        # E -> P
        return self.P()

    def S(self) -> Node:
        # S -> A
        return self.A()

    def A(self) -> Node:
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
        raise SyntaxError(f"Unexpected token {self.lexer.T.repr!r} at line {line}, column {col}: expected constant or '('")

    def P(self) -> Node:
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
