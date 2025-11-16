from .node import Node, NodeType
from .source import Source

from typing import Callable


def _c_div(a: int, b: int) -> int:
    """Integer division that truncates toward zero (like in C)."""
    quotient = abs(a) // abs(b)
    if (a < 0) ^ (b < 0):
        quotient = -quotient
    return quotient


def _c_mod(a: int, b: int) -> int:
    """Modulo operation that matches C behavior."""
    return a - _c_div(a, b) * b

class Optimizer:
    def __init__(self, source_code: Source = None, verbose: bool = False):
        self.source_code = source_code
        self.verbose = verbose

    def optimize_ast(self, node: Node | None) -> Node | None:
        """Optimize the AST with constant folding and dead code elimination."""
        if node is None:
            return None

        optimized_children: list[Node] = []
        for child in node.children:
            optimized = self.optimize_ast(child)
            if optimized is not None:
                optimized_children.append(optimized)
        node.children = optimized_children

        node = self._fold_constants(node)
        node = self._eliminate_dead_code(node)
        return node

    def optimize_asm(self, asm: list[str]) -> list[str]:
        """Optimize the generated assembly code (unused)."""
        # unused
        return asm

    def _fold_constants(self, node: Node) -> Node:
        if not node.children:
            return node

        # Unary operators
        if node.type in self._UNARY_FOLDERS:
            child = node.children[0]
            value = self._const_value(child)
            if value is None:
                return node
            folded = self._UNARY_FOLDERS[node.type](value)
            self._turn_into_const(node, folded)
            return node

        # Binary operators
        if node.type in self._BINARY_FOLDERS and len(node.children) >= 2:
            left_val = self._const_value(node.children[0])
            right_val = self._const_value(node.children[1])
            if left_val is None or right_val is None:
                return node

            # Skip folding on undefined operations (division/mod by zero)
            if node.type in {NodeType.NODE_DIV, NodeType.NODE_MOD} and right_val == 0:
                return node

            folded = self._BINARY_FOLDERS[node.type](left_val, right_val)
            self._turn_into_const(node, folded)
        return node

    def _eliminate_dead_code(self, node: Node | None) -> Node | None:
        if node is None:
            return None

        match node.type:
            case NodeType.NODE_DROP:
                if not node.children:
                    return None
                child = node.children[0]
                if self._const_value(child) is not None:
                    return None
                return node

            case NodeType.NODE_COND:
                if not node.children:
                    return None
                cond = node.children[0]
                cond_val = self._const_value(cond)
                if cond_val is None:
                    return node

                then_branch = node.children[1] if len(node.children) > 1 else None
                else_branch = node.children[2] if len(node.children) > 2 else None
                chosen = then_branch if cond_val != 0 else else_branch
                return chosen

            case NodeType.NODE_SEQ:
                flattened: list[Node] = []
                for child in node.children:
                    if child.type == NodeType.NODE_SEQ:
                        flattened.extend(child.children)
                    else:
                        flattened.append(child)
                node.children = flattened
                if not node.children:
                    return None
                if len(node.children) == 1:
                    return node.children[0]
                return node

            case NodeType.NODE_BLOCK:
                if not node.children:
                    return None
                return node

            case _:
                return node

    @staticmethod
    def _turn_into_const(node: Node, value: int) -> None:
        node.type = NodeType.NODE_CONST
        node.value = value
        node.children = []
        node.repr = None
        node.index = None

    @staticmethod
    def _const_value(node: Node | None) -> int | None:
        if node is None:
            return None
        if node.type == NodeType.NODE_CONST and node.value is not None:
            return node.value
        return None

    _UNARY_FOLDERS: dict[NodeType, Callable[[int], int]] = {
        NodeType.NODE_NEG: lambda x: -x,
        NodeType.NODE_NOT: lambda x: 0 if x != 0 else 1,
    }

    _BINARY_FOLDERS: dict[NodeType, Callable[[int, int], int]] = {
        NodeType.NODE_ADD: lambda a, b: a + b,
        NodeType.NODE_SUB: lambda a, b: a - b,
        NodeType.NODE_MUL: lambda a, b: a * b,
        NodeType.NODE_DIV: _c_div,
        NodeType.NODE_MOD: _c_mod,
        NodeType.NODE_AND: lambda a, b: 1 if (a != 0 and b != 0) else 0,
        NodeType.NODE_OR: lambda a, b: 1 if (a != 0 or b != 0) else 0,
        NodeType.NODE_EQ: lambda a, b: 1 if a == b else 0,
        NodeType.NODE_NOT_EQ: lambda a, b: 1 if a != b else 0,
        NodeType.NODE_LOWER: lambda a, b: 1 if a < b else 0,
        NodeType.NODE_LOWER_EQ: lambda a, b: 1 if a <= b else 0,
        NodeType.NODE_GREATER: lambda a, b: 1 if a > b else 0,
        NodeType.NODE_GREATER_EQ: lambda a, b: 1 if a >= b else 0,
    }
