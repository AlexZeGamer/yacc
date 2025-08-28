import argparse
from token import Token, TokenType

T: Token = None
T_prev: Token = None
source_code: str = ""
pos: int = 0

def main():
    """Main function to handle argument parsing and file reading."""
    parser = argparse.ArgumentParser(description="Yet Another C Compiler")
    parser.add_argument("input", nargs="?", help="Input file to compile")
    parser.add_argument("-i", "--input", dest="input", help="Input file to compile")
    parser.add_argument("-o", "--output", dest="output", default=None, help="Output file")
    args = parser.parse_args()

    if args.input is None:
        parser.print_help()
        return

    if args.output is None:
        args.output = args.input.rsplit('.', 1)[0] + '.out'

    print(f"Compiling {args.input} to {args.output}")

    with open(args.input, 'r') as f:
        global source_code
        source_code = f.read()

    next()  # lire le premier token

    with open(args.output, "w") as f:
        f.write("")  # clear the output file
    if T is not None:
        while T.type != TokenType.TOK_EOF:
            with open(args.output, "a") as f:
                f.write(f"{T}\n")
            next()

def pos_to_line_col(pos: int) -> tuple[int, int]:
    """Convert a position in the source code to (line, col) tuple."""
    line = 1
    col = 1
    for i in range(pos):
        if source_code[i] == '\n':
            line += 1
            col = 1
        else:
            col += 1
    return line, col

def next():
    """Read the next token from the source code and update global T and T_prev."""
    global T, T_prev, pos
    T_prev = T
    
    # skip whitespace
    # TODO: handle comments
    while pos < len(source_code) and source_code[pos].isspace():
        pos += 1

    if pos < len(source_code):
        current_char = source_code[pos]
        
        # number
        if current_char.isdigit():
            number_str = ''
            while pos < len(source_code) and source_code[pos].isdigit():
                number_str += source_code[pos]
                pos += 1
            T = Token(TokenType.TOK_CONST, int(number_str), number_str)
        
        # identifier
        elif current_char.isalpha() or current_char == '_':
            ident_str = ''
            while pos < len(source_code) and (source_code[pos].isalnum() or source_code[pos] == '_'):
                ident_str += source_code[pos]
                pos += 1
            
            if ident_str in Token.keywords:
                T = Token(Token.keywords[ident_str], repr=ident_str) # keyword
            else:
                T = Token(TokenType.TOK_IDENT, repr=ident_str) # identifier (variable name, function name, etc.)

        # other cases
        else:
            while pos < len(source_code) and not source_code[pos].isspace() and not source_code[pos].isalnum() and source_code[pos] != '_':
                current_char = source_code[pos]
                if pos + 1 < len(source_code):
                    # two-character operators
                    two_char_op = current_char + source_code[pos + 1]
                    if two_char_op in Token.operators:
                        T = Token(Token.operators[two_char_op], repr=two_char_op)
                        pos += 2
                        break
                # single-character operators
                if current_char in Token.operators:
                    T = Token(Token.operators[current_char], repr=current_char)
                    pos += 1
                    break
                pos += 1
            
            else:
                # unknown token
                T = Token(TokenType.TOK_UNKNOWN, repr=current_char)
    else:
        T = Token(TokenType.TOK_EOF)

def check(type: TokenType) -> bool:
    """Check if the current token is of the given type."""
    global T
    if T.type == type:
        next()
        return True
    return False

def accept(type: TokenType):
    """Accept the current token if it matches the given type, else raise an error."""
    if not check(type):
        line, col = pos_to_line_col(pos)
        raise SyntaxError(f"Unexpected token \"{T.repr}\" at line {line}, column {col}, expected \"{type}\"")

if __name__ == "__main__":
    main()
