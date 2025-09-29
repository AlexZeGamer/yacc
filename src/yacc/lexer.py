from .token import Token, TokenType
from .source import Source

class Lexer:
    def __init__(self, source_code: Source | str):
        self.source_code: Source = Source.from_path(source_code) if isinstance(source_code, str) else source_code
        self.pos: int = 0
        self.T: Token = None
        self.T_prev: Token = None
        self.next()

    def next(self) -> None:
        """Read the next token from the source code and update global T and T_prev."""
        self.T_prev = self.T
        
        # skip whitespace and comments
        while True:
            # skip whitespace
            while self.pos < len(self.source_code) and self.source_code[self.pos].isspace():
                self.pos += 1

            # handle comments
            if self.pos + 1 < len(self.source_code) and self.source_code[self.pos] == '/':
                nxt = self.source_code[self.pos + 1]

                # single-line comment: // ... (until EOL)
                if nxt == '/':
                    self.pos += 2
                    while self.pos < len(self.source_code) and self.source_code[self.pos] != '\n':
                        self.pos += 1
                    # loop again to skip following whitespace/comments
                    continue

                # multi-line comment: /* ... */
                if nxt == '*':
                    start_pos = self.pos
                    self.pos += 2
                    closed = False
                    while self.pos + 1 < len(self.source_code):
                        if self.source_code[self.pos:self.pos + 2] == '*/':
                            self.pos += 2
                            closed = True
                            break
                        self.pos += 1
                    if not closed:
                        line, col = self.source_code.pos_to_line_col(start_pos)
                        raise SyntaxError(f"Unterminated comment starting at line {line}, column {col}")
                    
                    # loop again to skip following whitespace/comments
                    continue

            break

        if self.pos < len(self.source_code):
            current_char = self.source_code[self.pos]

            # number
            if current_char.isdigit():
                number_str = ''
                while self.pos < len(self.source_code) and self.source_code[self.pos].isdigit():
                    number_str += self.source_code[self.pos]
                    self.pos += 1
                self.T = Token(TokenType.TOK_CONST, int(number_str), number_str)
            
            # identifier
            elif current_char.isalpha() or current_char == '_':
                ident_str = ''
                while self.pos < len(self.source_code) and (self.source_code[self.pos].isalnum() or self.source_code[self.pos] == '_'):
                    ident_str += self.source_code[self.pos]
                    self.pos += 1
                
                if ident_str in Token.keywords:
                    self.T = Token(Token.keywords[ident_str], repr=ident_str) # keyword
                else:
                    self.T = Token(TokenType.TOK_IDENT, repr=ident_str) # identifier (variable name, function name, etc.)

            # other cases
            else:
                while self.pos < len(self.source_code) and not self.source_code[self.pos].isspace() and not self.source_code[self.pos].isalnum() and self.source_code[self.pos] != '_':
                    current_char = self.source_code[self.pos]
                    if self.pos + 1 < len(self.source_code):
                        # two-character operators
                        two_char_op = current_char + self.source_code[self.pos + 1]
                        if two_char_op in Token.operators:
                            self.T = Token(Token.operators[two_char_op], repr=two_char_op)
                            self.pos += 2
                            break
                    # single-character operators
                    if current_char in Token.operators:
                        self.T = Token(Token.operators[current_char], repr=current_char)
                        self.pos += 1
                        break
                    self.pos += 1
                
                else:
                    # unknown token
                    self.T = Token(TokenType.TOK_UNKNOWN, repr=current_char)
        else:
            self.T = Token(TokenType.TOK_EOF)

    def check(self, type: TokenType) -> bool:
        """Check if the current token is of the given type."""
        if self.T.type == type:
            self.next()
            return True
        return False

    def accept(self, type: TokenType) -> None:
        """Accept the current token if it matches the given type, else raise an error."""
        if not self.check(type):
            line, col = self.source_code.pos_to_line_col(self.pos)
            raise SyntaxError(f"Unexpected token \"{self.T.repr}\" at line {line}, column {col}, expected \"{type}\"")
