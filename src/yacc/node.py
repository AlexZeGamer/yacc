from enum import Enum, auto
from typing import Self

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
            result += " " + str(child)
        result += ")"
        return result
    
    def _str_beautify(self) -> str:
        """Return a beautified string representation of the tree (written with ChatGPT)."""
        def label(n: Self) -> str:
            if n.repr is not None:
                return f"{n.type.name} {n.repr}"
            if n.value is not None:
                return f"{n.type.name} {n.value}"
            return n.type.name

        lines: list[str] = []

        def walk(n: Self, prefix: str = "", is_last: bool = True):
            conn = "" if prefix == "" else ("└── " if is_last else "├── ")
            lines.append(prefix + conn + label(n))
            if n.children:
                child_prefix = prefix + ("    " if is_last else "│   ")
                last_idx = len(n.children) - 1
                for i, ch in enumerate(n.children):
                    walk(ch, child_prefix, i == last_idx)

        walk(self)
        return "\n".join(lines)

    def print(self, beautify: bool = True):
        if beautify:
            print(self._str_beautify())
        else:
            print(str(self))

    def __repr__(self):
        parts = [f"Node(type={self.type.name}"]
        if self.value is not None:
            parts.append(f", value={self.value}")
        if self.repr is not None:
            parts.append(f", repr={self.repr!r}")
        parts.append(f", children={len(self.children)})")
        return "".join(parts)

    def __len__(self):
        return len(self.children)

    def add_child(self, child: Self):
        self.children.append(child)
