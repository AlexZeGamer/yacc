import argparse
from .token import Token, TokenType

T = None
T_prev = None
source_code = ""
pos = 0

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
    T_prev: Token = T
    
    while pos < len(source_code) and source_code[pos].isspace():
        pos += 1

    if pos < len(source_code):
        current_char = source_code[pos]
        
        # Lire un nombre
        if current_char.isdigit():
            start_pos = pos
            while pos < len(source_code) and source_code[pos].isdigit():
                pos += 1
            number_str = source_code[start_pos:pos]
            T = Token(TokenType.TOK_CONST, int(number_str), number_str)
        
        # Lire un identificateur
        elif current_char.isalpha():
            start_pos = pos
            while pos < len(source_code) and (source_code[pos].isalnum() or source_code[pos] == '_'):
                pos += 1
            ident_str = source_code[start_pos:pos]
            if ident_str in TokenType.__members__:
                T = Token(TokenType[ident_str], repr=ident_str)
            else:
                T = Token(TokenType.TOK_IDENT, repr=ident_str)

        # Gérer les autres cas
        else:
            ...
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
