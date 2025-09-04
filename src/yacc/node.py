from enum import Enum, auto
from typing import Self

from .token import TokenType

class NodeType(Enum):
    NODE_UNKNOWN = auto()      # unknown node

    # Constant nodes
    NODE_CONST = auto()        # constant node (integer)

    # Unary operators
    NODE_NOT = auto()          # NOT node
    NODE_NEG = auto()          # negation node (unary minus)

    # Arithmetic binary operators
    NODE_ADD = auto()          # addition
    NODE_SUB = auto()          # subtraction
    NODE_MUL = auto()          # multiplication
    NODE_DIV = auto()          # division
    NODE_MOD = auto()          # modulo

    # Logical binary operators
    NODE_AND = auto()          # logical AND
    NODE_OR = auto()           # logical OR

    # Comparison operators
    NODE_EQ = auto()           # ==
    NODE_NOT_EQ = auto()       # !=
    NODE_LOWER = auto()        # <
    NODE_LOWER_EQ = auto()     # <=
    NODE_GREATER = auto()      # >
    NODE_GREATER_EQ = auto()   # >=

    # Assignment
    NODE_AFFECT = auto()       # =

    # Statements / blocks / debugging
    NODE_DEBUG = auto()        # debug E;
    NODE_BLOCK = auto()        # { I* }
    NODE_DROP = auto()         # E;  (evaluate and drop)

class Node:
    def __init__(self, nd_type: NodeType, value: int = None, children: list[Self] = []):
        self.type: NodeType = nd_type
        self.value: int = value
        self.repr: str = None
        self.children: list[Self] = children

    # Dictionary of binary operators for priority parsing
    # operator: (priority, priority for right argument, corresponding NodeType)
    OP: dict[TokenType, dict[str, object]] = {
        # (highest)
        # Level 7 : *, /, %
        TokenType.TOK_MUL:        {"prio": 7, "prio_arg": 8, "ntype": NodeType.NODE_MUL        },
        TokenType.TOK_DIV:        {"prio": 7, "prio_arg": 8, "ntype": NodeType.NODE_DIV        },
        TokenType.TOK_MOD:        {"prio": 7, "prio_arg": 8, "ntype": NodeType.NODE_MOD        },
        # Level 6 : +, -
        TokenType.TOK_ADD:        {"prio": 6, "prio_arg": 7, "ntype": NodeType.NODE_ADD        },
        TokenType.TOK_SUB:        {"prio": 6, "prio_arg": 7, "ntype": NodeType.NODE_SUB        },
        # Level 5 : <, <=, >, >=
        TokenType.TOK_LOWER:      {"prio": 5, "prio_arg": 6, "ntype": NodeType.NODE_LOWER      },
        TokenType.TOK_LOWER_EQ:   {"prio": 5, "prio_arg": 6, "ntype": NodeType.NODE_LOWER_EQ   },
        TokenType.TOK_GREATER:    {"prio": 5, "prio_arg": 6, "ntype": NodeType.NODE_GREATER    },
        TokenType.TOK_GREATER_EQ: {"prio": 5, "prio_arg": 6, "ntype": NodeType.NODE_GREATER_EQ },
        # Level 4 : ==, !=
        TokenType.TOK_EQ:         {"prio": 4, "prio_arg": 5, "ntype": NodeType.NODE_EQ         },
        TokenType.TOK_NOT_EQ:     {"prio": 4, "prio_arg": 5, "ntype": NodeType.NODE_NOT_EQ     },
        # Level 3 : &&
        TokenType.TOK_AND:        {"prio": 3, "prio_arg": 4, "ntype": NodeType.NODE_AND        },
        # Level 2 : ||
        TokenType.TOK_OR:         {"prio": 2, "prio_arg": 3, "ntype": NodeType.NODE_OR         },
        # Level 1 : =
        TokenType.TOK_AFFECT:     {"prio": 1, "prio_arg": 1, "ntype": NodeType.NODE_AFFECT     },
        # (lowest)
    }

    # Dictionary of "easy nodes" for code generation
    # NodeType: (prefix_code, suffix_code)
    EN: dict[NodeType, tuple[str, str]] = {
        NodeType.NODE_NOT:        (""      , "not"   ),
        NodeType.NODE_NEG:        ("push 0", "sub"   ),
        # binary ops
        NodeType.NODE_ADD:        (""      , "add"   ),
        NodeType.NODE_SUB:        (""      , "sub"   ),
        NodeType.NODE_MUL:        (""      , "mul"   ),
        NodeType.NODE_DIV:        (""      , "div"   ),
        NodeType.NODE_MOD:        (""      , "mod"   ),
        NodeType.NODE_AND:        (""      , "and"   ),
        NodeType.NODE_OR:         (""      , "or"    ),
        NodeType.NODE_EQ:         (""      , "cmpeq" ),
        NodeType.NODE_NOT_EQ:     (""      , "cmpne" ),
        NodeType.NODE_LOWER:      (""      , "cmplt" ),
        NodeType.NODE_LOWER_EQ:   (""      , "cmple" ),
        NodeType.NODE_GREATER:    (""      , "cmpgt" ),
        NodeType.NODE_GREATER_EQ: (""      , "cmpge" ),
        # statements / helpers
        NodeType.NODE_DEBUG:      (""      , "dbg"   ),
        NodeType.NODE_BLOCK:      (""      , ""      ),  # children will just be added to the code with the loop
        NodeType.NODE_DROP:       (""      , "drop 1"),
    }

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
