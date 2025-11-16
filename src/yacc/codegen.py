from .node import Node, NodeType
from .source import Source

from .utils.errors import CompilationError

class CodeGenerator:
    def __init__(self, output_path: str = None, to_stdout: bool = False, source_code: Source = None, verbose: bool = False) -> None:
        self._lines: list[str] = []
        self._is_open: bool = False
        self.output_path = output_path
        self._to_stdout = to_stdout
        self.source_code = source_code
        self.verbose = verbose
        self._label_counter: int = 0
        self._loop_stack: list[dict[str, str]] = []

    def add_line(self, line: str) -> None:
        """Add one line to the buffer"""
        self._lines.append(line)

    def _start(self) -> None:
        """Start generation and add the prefix line"""
        if self._is_open:
            return
        self._is_open = True

        self._lines = []
        self._label_counter = 0
        self._loop_stack = []
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
        if nbVars:
            self.add_line(f"resn {nbVars}") # reserve space for variables
        self.gennode(node)
        if nbVars:
            self.add_line(f"drop {nbVars}") # clean up variable space

    def gennode(self, node: Node) -> None:
        """Generate code for a single AST node (recursive)"""
        match node.type:
            case NodeType.NODE_AFFECT:
                self.gennode(node.children[1])
                self.add_line("dup")
                self.add_line(f"set {node.children[0].index}")

            case NodeType.NODE_COND:
                label_id = self._next_label_id()
                false_label = self._format_label(label_id, "else")
                end_label = self._format_label(label_id, "end")

                # evaluate condition
                self.gennode(node.children[0])

                # if false, jump to else (or end if no else)
                self.add_line(f"jumpf {false_label}")
                self.gennode(node.children[1])

                # (optional) else instruction
                if len(node.children) > 2 and node.children[2] is not None:
                    self.add_line(f"jump {end_label}")
                    self.add_line(f".{false_label}")
                    self.gennode(node.children[2])
                    self.add_line(f".{end_label}")
                else:
                    self.add_line(f".{false_label}")

            case NodeType.NODE_LOOP:
                loop_id = self._next_label_id()
                head_label = self._format_label(loop_id, "loop_start")
                continue_label = self._format_label(loop_id, "loop_continue")
                end_label = self._format_label(loop_id, "loop_end")

                self._loop_stack.append({
                    "continue": continue_label,
                    "end": end_label,
                    "head": head_label,
                })

                self.add_line(f".{head_label}")
                for child in node.children:
                    self.gennode(child)
                self.add_line(f"jump {head_label}")
                self.add_line(f".{end_label}")

                self._loop_stack.pop()

            case NodeType.NODE_BREAK:
                loop_info = self._current_loop()
                self.add_line(f"jump {loop_info['end']}")

            case NodeType.NODE_CONTINUE:
                loop_info = self._current_loop()
                self.add_line(f"jump {loop_info['continue']}")

            case NodeType.NODE_TARGET:
                loop_info = self._current_loop()
                if node.value:
                    self.add_line(f".{loop_info['continue']}")
                else:
                    loop_info["continue"] = loop_info["head"]

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

    def _next_label_id(self) -> int:
        label_id = self._label_counter
        self._label_counter += 1
        return label_id

    @staticmethod
    def _format_label(label_id: int, suffix: str) -> str:
        return f"L{label_id}_{suffix}"

    def _current_loop(self) -> dict[str, str]:
        if not self._loop_stack:
            raise CompilationError("Loop control statement used outside of a loop")
        return self._loop_stack[-1]
