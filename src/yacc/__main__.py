import argparse

from source import Source
from lexer import Lexer

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

    source_code: Source = Source.from_path(args.input)

    lexer = Lexer(source_code)
    with open(args.output, "w") as f:
        f.write("")  # clear the output file
    from token import TokenType
    if lexer.T is not None:
        while lexer.T.type != TokenType.TOK_EOF:
            with open(args.output, "a") as f:
                f.write(f"{lexer.T}\n")
            lexer.next()

if __name__ == "__main__":
    main()
