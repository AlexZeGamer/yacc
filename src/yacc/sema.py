from .node import Node, NodeType
from .symbol import SymbolTable
from .source import Source

from .utils.errors import CompilationError
from .utils.logger import Logger

class SemanticAnalyzer:
    def __init__(self, symbol_table: SymbolTable = None, source_code: Source = None, verbose: bool = False):
        self.symbol_table = symbol_table or SymbolTable()
        self.source_code = source_code
        self.verbose = verbose
        self._loop_depth: int = 0
        self._functions: set[str] = set()
        self._current_function: Node | None = None

    def analyze(self, node: Node) -> Node:
        if node is None:
            return None

        if node.type == NodeType.NODE_FUNCTION:
            self._analyze_function(node)
        else:
            self._reset_state()
            self.symbol_table.start_scope()
            try:
                self._analyze_node(node)
            finally:
                self.symbol_table.end_scope()

        if self.verbose:
            Logger.log("Semantic analysis (AST with symbol info):")
            node.print(mode="beautify")

        return node

    def _analyze_function(self, node: Node) -> None:
        self._register_function(node.repr)

        previous_function = self._current_function
        self._current_function = node

        self._reset_state()
        self.symbol_table.start_scope()

        param_count = max(len(node.children) - 1, 0)
        try:
            # analyze parameters (declare) + body
            for child in node.children[:-1]:
                self._analyze_node(child)
            if node.children:
                self._analyze_node(node.children[-1])

            node.value = max(self.symbol_table.nbVars - param_count, 0)
        finally:
            self.symbol_table.end_scope()
            self._current_function = previous_function

    def _reset_state(self) -> None:
        self.symbol_table.nbVars = 0
        self.symbol_table.scopes = []
        self._loop_depth = 0

    def _register_function(self, name: str | None) -> None:
        if name is None:
            raise CompilationError("Anonymous functions are not allowed")
        if name == "start":
            raise CompilationError("Function name 'start' is reserved")
        if name in self._functions:
            raise CompilationError(f"Function '{name}' is already defined")
        self._functions.add(name)

    def _analyze_node(self, node: Node) -> None:
        match node.type:
            case NodeType.NODE_BLOCK:
                self.symbol_table.start_scope()
                for child in node.children:
                    self._analyze_node(child)
                self.symbol_table.end_scope()

            case NodeType.NODE_LOOP:
                self.symbol_table.start_scope()
                self._loop_depth += 1
                for child in node.children:
                    self._analyze_node(child)
                self._loop_depth -= 1
                self.symbol_table.end_scope()

            case NodeType.NODE_SEQ:
                for child in node.children:
                    self._analyze_node(child)

            case NodeType.NODE_DECLARE:
                try:
                    self.symbol_table.declare(node.repr)
                except ValueError as e:
                    raise CompilationError(str(e))

            case NodeType.NODE_REF:
                symbol = self.symbol_table.find(node.repr)
                node.index = symbol.index

            case NodeType.NODE_AFFECT:
                if node.children[0].type != NodeType.NODE_REF:
                    raise ValueError(f"{node.children[0].repr} is not a variable")
                for child in node.children:
                    self._analyze_node(child)

            case NodeType.NODE_BREAK | NodeType.NODE_CONTINUE:
                if self._loop_depth == 0:
                    keyword = "break" if node.type == NodeType.NODE_BREAK else "continue"
                    raise CompilationError(f"'{keyword}' used outside of a loop")

            case NodeType.NODE_COND:
                self._analyze_node(node.children[0]) # condition
                self._analyze_node(node.children[1]) # then branch
                if len(node.children) > 2:
                    self._analyze_node(node.children[2]) # else branch

            case NodeType.NODE_RETURN:
                if self._current_function is None:
                    raise CompilationError("'return' used outside of a function")
                for child in node.children:
                    self._analyze_node(child)

            case NodeType.NODE_CALL:
                if not node.children:
                    raise CompilationError("Malformed function call")
                callee = node.children[0]
                if callee.type != NodeType.NODE_REF:
                    raise CompilationError("Function call target must be an identifier")
                # Do not resolve callee in the variable symbol table.
                for arg in node.children[1:]:
                    self._analyze_node(arg)

            case NodeType.NODE_FUNCTION:
                raise CompilationError("Nested function definitions are not supported")

            case _:
                for child in node.children:
                    self._analyze_node(child)
