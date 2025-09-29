from .node import Node, NodeType
from .source import Source

from .utils.errors import CompilationError

class CodeGenerator:
    def __init__(self, output_path: str = None, to_stdout: bool = False, source_code: Source = None) -> None:
        self._lines: list[str] = []
        self._is_open: bool = False
        self.output_path = output_path
        self._to_stdout = to_stdout
        self.source_code = source_code

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

    def _finalize(self) -> None:
        """End generation by adding suffix lines and write to file or stdout."""
        if not self._is_open:
            return

        self.add_line("halt")   # stop execution

        self._is_open = False

        asm = "\n".join(self._lines) + "\n"
        if self._to_stdout:
            print(asm, end="")
        elif self.output_path is not None:
            with open(self.output_path, "w", encoding="utf-8") as f:
                f.write(asm)
        else:
            raise ValueError("No output path specified for code generation.")

    def codegen(self, node: Node, nbVars: int = 0) -> None:
        """One code generation step (entry point of the compilation pipeline)"""
        self.add_line(f"resn {nbVars}") # reserve space for variables
        self.gennode(node)
        self.add_line(f"drop {nbVars}") # clean up variable space

    def gennode(self, node: Node) -> None:
        """Generate code for a single AST node (recursive)"""
        match node.type:
            case NodeType.NODE_AFFECT:
                self.gennode(node.children[1])
                self.add_line("dup")
                self.add_line(f"set {node.children[0].index}")

            case _ if node.type in Node.EN:
                prefix, suffix = Node.EN[node.type]
                if prefix:
                    self.add_line(self._expand(prefix, node))
                for child in node.children:
                    self.gennode(child)
                if suffix:
                    self.add_line(self._expand(suffix, node))

            case _:
                raise CompilationError(f"Code generation not implemented for node type: {node.type.name}")

    @staticmethod
    def _expand(template: str, node: Node) -> str:
        """
        Expand a template string by replacing placeholders.

        Placeholders:
        - '@': the node index if defined, otherwise the first child's index if any, else '0'
        - '#': the node value
        """
        at_value = None
        if node.index is not None:
            at_value = str(node.index)
        elif node.children and node.children[0].index is not None:
            # use the first child's index as a fallback
            # this is useful for nodes that do not store their own index
            # (e.g., ND_AFFECT nodes use the index of their ND_REF child)
            at_value = str(node.children[0].index)

        hash_value = str(node.value)

        if (
            (at_value is None and "@" in template) or
            (hash_value is None and "#" in template)
        ):
            raise ValueError(f"Cannot expand template: \"{template}\" with node: {node.__repr__()}")
    
        expanded = template
        if at_value is not None:
            expanded = expanded.replace("@", at_value)
        if hash_value is not None:
            expanded = expanded.replace("#", hash_value)

        return expanded
