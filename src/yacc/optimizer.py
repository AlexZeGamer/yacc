from .node import Node
from .source import Source

class Optimizer:
    def __init__(self, source_code: Source = None):
        self.source_code = source_code

    def optimize(self, node: Node) -> Node:
        return node
