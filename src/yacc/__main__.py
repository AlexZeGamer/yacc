import argparse

from source import Source
from lexer import Lexer
from token import TokenType
from parser import Parser
from sema import SemanticAnalyzer
from optimizer import Optimizer
from codegen import CodeGenerator

def main():
    """Main function to handle argument parsing and compilation pipeline."""
    args = parse_args()

    # print(f"Compiling to {'stdout' if args.to_stdout else args.output}")

    lexer = Lexer(args.source_code)
    if lexer.T is None:
        print("No tokens found.")
        return

    parser = Parser(lexer)
    sema = SemanticAnalyzer()
    optimizer = Optimizer()
    if args.to_stdout:
        codegen = CodeGenerator(to_stdout=True)
    else:
        codegen = CodeGenerator(output_path=args.output)

    codegen._start()
    while lexer.T.type != TokenType.TOK_EOF:
        codegen.codegen(parser, sema, optimizer)
    codegen._finalize()


def parse_args() -> argparse.Namespace:
    """Build the CLI, parse arguments, validate inputs, and resolve source/output."""
    ap = argparse.ArgumentParser(description="Yet Another C Compiler")
    # File input can be provided either as positional or via -i/--input
    # Positional input file (distinct name to avoid clashing with -i/--input)
    ap.add_argument("input_pos", nargs="?", help="Input file to compile (positional)")
    ap.add_argument("-i", "--input", dest="input", help="Input file to compile")
    ap.add_argument("-o", "--output", dest="output", default=None, help="Output file path")
    ap.add_argument("--stdout", dest="to_stdout", action="store_true", help="Print generated assembly to stdout instead of writing to a file")
    mx = ap.add_mutually_exclusive_group()
    mx.add_argument("--string", "--str", dest="input_string", default=None, help="Compile code provided as a string")
    mx.add_argument("--stdin", dest="read_stdin", action="store_true", help="Read input code from standard input")
    args = ap.parse_args()

    # Check that only one input source is given: positional, -i/--input, --string, --stdin
    provided = [
        args.input_pos is not None,
        args.input is not None,
        args.input_string is not None,
        bool(args.read_stdin),
    ]
    count = sum(1 for x in provided if x)
    if count == 0:
        ap.error("No input provided. Provide exactly one of: file (positional), -i/--input, --string, or --stdin.")
    if count > 1:
        ap.error("Multiple inputs provided. Provide exactly one of: file (positional), -i/--input, --string, or --stdin.")

    # Determine source of input
    input_path = None
    if args.input_pos is not None:
        input_path = args.input_pos
        source_code = Source.from_path(input_path)
    elif args.input is not None:
        input_path = args.input
        source_code = Source.from_path(input_path)
    elif args.input_string is not None:
        source_code = Source.from_string(args.input_string, name="<string>")
    else:
        source_code = Source.from_stdin()

    # Determine output path if not printing to stdout
    if args.output is None and not args.to_stdout:
        if input_path is not None:
            args.output = input_path.rsplit('.', 1)[0] + '.out'
        else:
            args.output = 'a.out'

    # Attach derived items to args for the rest of the pipeline
    args.source_code = source_code
    args.input_path = input_path

    return args


if __name__ == "__main__":
    main()
