from .node import Node
from .source import Source

class Optimizer:
    def __init__(self, source_code: Source = None, verbose: bool = False):
        self.source_code = source_code
        self.verbose = verbose

    def optimize_ast(self, node: Node) -> Node:
        # TODO
        return node
    
    def optimize_asm(self, asm: list[str]) -> list[str]:
        # TODO
        return asm
