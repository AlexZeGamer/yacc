import argparse

from source import Source
from lexer import Lexer
from token import TokenType
from parser import Parser
from sema import SemanticAnalyzer
from optimizer import Optimizer
from codegen import CodeGenerator

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

    # print(f"Compiling {args.input} to {args.output}")

    source_code: Source = Source.from_path(args.input)

    lexer = Lexer(source_code)
    if lexer.T is None:
        print("No tokens found.")
        return

    parser = Parser(lexer)
    sema = SemanticAnalyzer()
    optimizer = Optimizer()
    codegen = CodeGenerator()

    codegen._start()
    while lexer.T.type != TokenType.TOK_EOF:
        codegen.codegen(parser, sema, optimizer)
    codegen._close(args.output)

if __name__ == "__main__":
    main()
