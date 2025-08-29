from node import Node, NodeType

class CodeGenerator:
    def __init__(self):
        self._lines: list[str] = []
        self._is_open: bool = False

    def add_line(self, line: str) -> None:
        """Add one line to the buffer"""
        self._lines.append(line)

    def _start(self) -> None:
        """Start generation and add the prefix line"""
        if self._is_open:
            return
        self._is_open = True

        self._lines = []
        self.add_line(".start")

    def _close(self, output_path: str) -> None:
        """End generation by adding suffix lines and writing generated assembly code to file"""
        if not self._is_open:
            return
        
        self.add_line("dbg")    # show the result in the end (takes the top of the stack)
        self.add_line("halt")   # stop execution

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(self._lines) + "\n")
        
        self._is_open = False

    def codegen(self, parser, sema, optimizer) -> None:
        """One code generation step"""
        A = optimizer.optimize(sema.analyze(parser.parse()))
        if A is not None:
            self.gennode(A)

    def gennode(self, node) -> None:
        """Generate code for a single AST node (recursive)"""

        match node.type:
            case NodeType.NODE_CONST:
                self.add_line(f"push {node.value}")
            case NodeType.NODE_NOT:
                if node.children:
                    self.gennode(node.children[0])
                self.add_line("not")
            case NodeType.NODE_NEG:
                self.add_line("push 0")
                if node.children:
                    self.gennode(node.children[0])
                self.add_line("sub")
            case _:
                pass
