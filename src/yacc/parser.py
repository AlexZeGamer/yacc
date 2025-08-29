from token import Token, TokenType
from node import Node, NodeType
from lexer import Lexer

class Parser:
    def __init__(self, lexer: Lexer = None):
        self.lexer = lexer or Lexer("")
        self.current_token: Token = lexer.T

    def parse(self) -> Node:
        """One step of parsing"""
        if self.lexer.T is None or self.lexer.T.type == TokenType.TOK_EOF:
            return None

        # TODO