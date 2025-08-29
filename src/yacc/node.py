from enum import Enum, auto
from typing import Self

from matplotlib.pylab import f

class NodeType(Enum):
    NODE_UNKNOWN = auto()      # noeud inconnu

    NODE_CONST = auto()        # noeud constante (entier)
    NODE_NOT = auto()          # noeud NOT
    NODE_NEG = auto()          # noeud négation (moins unaire)

    # TODO

class Node:
    def __init__(self, nd_type: NodeType, value: int = None, children: list[Self] = []):
        self.type: NodeType = nd_type
        self.value: int = value
        self.repr: str = None
        self.children: list[Self] = children

    def __str__(self):
        result = "(" + self.type.name
        for child in self.children:
            result += "\n " + str(child)
        result += "\n)"
        return result

    def __repr__(self):
        return (
            f"Node(type={self.type.name}"
            f", value={self.value}" if self.value is not None else ""
            f", repr={self.repr!r}" if self.repr is not None else ""
            f", children={len(self.children)})"
        )

    def __len__(self):
        return len(self.children)

    def add_child(self, child: Self):
        self.children.append(child)
    