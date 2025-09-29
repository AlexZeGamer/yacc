from enum import Enum, auto
from typing import Self

from .token import TokenType

from .utils.logger import Logger

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
    NODE_EQ = auto()           # a == b
    NODE_NOT_EQ = auto()       # a != b
    NODE_LOWER = auto()        # a <  b
    NODE_LOWER_EQ = auto()     # a <= b
    NODE_GREATER = auto()      # a >  b
    NODE_GREATER_EQ = auto()   # a >= b

    # Symbols
    NODE_DECLARE = auto()         # declaration of a variable
    NODE_REF = auto()          # reference to a variable
    NODE_AFFECT = auto()       # a = b (assignment)

    # Statements / blocks / debugging
    NODE_DEBUG = auto()        # debug E;
    NODE_BLOCK = auto()        # { I* }
    NODE_DROP = auto()         # E;  (evaluate and drop)

class Node:
    def __init__(self, nd_type: NodeType, value: int = None, repr: int = None, index: int = None, children: list[Self] = []):
        self.type: NodeType = nd_type
        self.value: int = value
        self.repr: str = repr
        self.index: int = index
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
    # @ = index of variable, # = value of constant
    EN: dict[NodeType, tuple[str, str]] = {
        # constants
        NodeType.NODE_CONST:      ("push #", ""      ),
        # unary ops
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
        # symbols
        NodeType.NODE_DECLARE:    (""      , ""      ),  # no code needed
        NodeType.NODE_REF:        ("get @" , ""      ),  # get @index
        # statements / helpers
        NodeType.NODE_DEBUG:      (""      , "dbg"   ),
        NodeType.NODE_BLOCK:      (""      , ""      ),  # children will just be added to the code with the loop
        NodeType.NODE_DROP:       (""      , "drop 1"),
    }

    def __str__(self) -> str:
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

    def print(self, beautify: bool = True) -> None:
        if beautify:
            Logger.log(self._str_beautify())
        else:
            Logger.log(str(self))

    def __repr__(self) -> str:
        parts = [f"Node(type={self.type.name}"]
        if self.value is not None:
            parts.append(f", value={self.value}")
        if self.repr is not None:
            parts.append(f", repr={self.repr!r}")
        parts.append(f", children={len(self.children)})")
        return "".join(parts)

    def __len__(self) -> int:
        return len(self.children)

    def add_child(self, child: Self) -> None:
        self.children.append(child)
