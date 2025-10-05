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

    def analyze(self, node: Node) -> Node:
        self.symbol_table.nbVars = 0

        self._analyze_node(node)
        if self.verbose:
            Logger.log("Semantic analysis (AST with symbol info):")
            node.print(mode="beautify")
        
        return node

    def _analyze_node(self, node: Node) -> None:
        match node.type:
            case NodeType.NODE_BLOCK:
                self.symbol_table.start_scope()
                for child in node.children:
                    self._analyze_node(child)
                self.symbol_table.end_scope()

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

            case NodeType.NODE_COND:
                self._analyze_node(node.children[0]) # condition
                self._analyze_node(node.children[1]) # then branch
                if len(node.children) > 2:
                    self._analyze_node(node.children[2]) # else branch

            case _:
                for child in node.children:
                    self._analyze_node(child)
