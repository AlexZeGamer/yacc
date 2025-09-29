from .node import Node
from .source import Source

class Optimizer:
    def __init__(self, source_code: Source = None, verbose: bool = False):
        self.source_code = source_code
        self.verbose = verbose

    def optimize(self, node: Node) -> Node:
        return node
