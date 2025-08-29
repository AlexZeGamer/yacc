from enum import Enum, auto

class TokenType(Enum):
    TOK_UNKNOWN = auto()       # token inconnu

    TOK_EOF = auto()           # end of file
    TOK_CONST = (auto())       # constantes (entiers, pas besoin de gérer les réels etc) + valeur associée
    TOK_IDENT = auto()         # identificateurs (variables, ...) + chaine associée

    # Opérateurs arithmétiques
    TOK_ADD = auto()           # +
    TOK_SUB = auto()           # -
    TOK_MUL = auto()           # *
    TOK_DIV = auto()           # /
    TOK_MOD = auto()           # %

    # Opérateurs logiques
    TOK_AND = auto()           # &&
    TOK_OR = auto()            # ||
    TOK_NOT = auto()           # !

    # Opérateurs de comparaison
    TOK_EQ = auto()            # ==
    TOK_NOT_EQ = auto()        # !=
    TOK_LOWER = auto()         # <
    TOK_LOWER_EQ = auto()      # <=
    TOK_GREATER = auto()       # >
    TOK_GREATER_EQ = auto()    # >=

    # Parenthesage
    TOK_LPARENTHESIS = auto()  # (
    TOK_RPARENTHESIS = auto()  # )
    TOK_LBRACKET = auto()      # [
    TOK_RBRACKET = auto()      # ]
    TOK_LBRACE = auto()        # {
    TOK_RBRACE = auto()        # }

    # Affectation
    TOK_AFFECT = auto()        # =

    # Séparateurs
    TOK_SEMICOLON = auto()     # ;
    TOK_COMMA = auto()         # ,

    # Adresse et valeur
    TOK_ADDRESS = auto()       # &

    # Mots-clés
    TOK_INT = auto()           # int
    TOK_VOID = auto()          # void
    TOK_RETURN = auto()        # return
    TOK_IF = auto()            # if
    TOK_ELSE = auto()          # else
    TOK_FOR = auto()           # for
    TOK_DO = auto()            # do
    TOK_WHILE = auto()         # while
    TOK_BREAK = auto()         # break
    TOK_CONTINUE = auto()      # continue

    # Mots-clés supplémentaires
    TOK_DEBUG = auto()         # debug
    TOK_SEND = auto()          # send
    TOK_RECV = auto()          # recv


class Token:
    keywords = {
        "int": TokenType.TOK_INT,
        "void": TokenType.TOK_VOID,
        "return": TokenType.TOK_RETURN,
        "if": TokenType.TOK_IF,
        "else": TokenType.TOK_ELSE,
        "for": TokenType.TOK_FOR,
        "do": TokenType.TOK_DO,
        "while": TokenType.TOK_WHILE,
        "break": TokenType.TOK_BREAK,
        "continue": TokenType.TOK_CONTINUE,
        "debug": TokenType.TOK_DEBUG,
        "send": TokenType.TOK_SEND,
        "recv": TokenType.TOK_RECV,
    }

    operators = {
        "+": TokenType.TOK_ADD,
        "-": TokenType.TOK_SUB,
        "*": TokenType.TOK_MUL,
        "/": TokenType.TOK_DIV,
        "%": TokenType.TOK_MOD,
        "&&": TokenType.TOK_AND,
        "||": TokenType.TOK_OR,
        "!": TokenType.TOK_NOT,
        "==": TokenType.TOK_EQ,
        "!=": TokenType.TOK_NOT_EQ,
        "<": TokenType.TOK_LOWER,
        "<=": TokenType.TOK_LOWER_EQ,
        ">": TokenType.TOK_GREATER,
        ">=": TokenType.TOK_GREATER_EQ,
        "(": TokenType.TOK_LPARENTHESIS,
        ")": TokenType.TOK_RPARENTHESIS,
        "[": TokenType.TOK_LBRACKET,
        "]": TokenType.TOK_RBRACKET,
        "{": TokenType.TOK_LBRACE,
        "}": TokenType.TOK_RBRACE,
        "=": TokenType.TOK_AFFECT,
        ";": TokenType.TOK_SEMICOLON,
        ",": TokenType.TOK_COMMA,
        "&": TokenType.TOK_ADDRESS,
    }

    def __init__(self, tok_type: TokenType, value: int = None, repr: str = None):
        self.type: TokenType = tok_type
        self.value: int = value
        self.repr: str = repr

    def __str__(self):
        return (
            f"Token: "
            f"type = {self.type.name:<18} "
            f"value = {self.value!s:<10} "
            f"repr = {self.repr.replace('\n', '\\n') if self.repr else None}"
        )
    
    def __repr__(self):
        return (
            f"Token(type={self.type}, value={self.value}, repr={self.repr.replace('\n', '\\n') if self.repr else None})"
        )
