from .node import Node, NodeType
from .source import Source

class SemanticAnalyzer:
    def __init__(self, source_code: Source = None):
        self.source_code = source_code

    def analyze(self, node: Node) -> Node:
        return node
