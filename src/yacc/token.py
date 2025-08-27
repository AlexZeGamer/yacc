from enum import Enum, auto

class TokenType(Enum):
    TOK_EOF = auto()  # end of file
    TOK_CONST = (
        auto()
    )  # constantes (entiers, pas besoin de gérer les réels etc) + valeur associée
    TOK_IDENT = auto()  # identificateurs (variables, ...) + chaine associée

    # Opérateurs arithmétiques
    TOK_ADD = auto()  # +
    TOK_SUB = auto()  # -
    TOK_MUL = auto()  # *
    TOK_DIV = auto()  # /
    TOK_MOD = auto()  # %

    # Opérateurs logiques
    TOK_AND = auto()  # &&
    TOK_OR = auto()  # ||
    TOK_NOT = auto()  # !

    # Opérateurs de comparaison
    TOK_EQ = auto()  # ==
    TOK_NOT_EQ = auto()  # !=
    TOK_LOWER = auto()  # <
    TOK_LOWER_EQ = auto()  # <=
    TOK_GREATER = auto()  # >
    TOK_GREATER_EQ = auto()  # >=

    # Parenthesage
    TOK_LPARENTHESIS = auto()  # (
    TOK_RPARENTHESIS = auto()  # )
    TOK_LBRACKET = auto()  # [
    TOK_RBRACKET = auto()  # ]
    TOK_LBRACE = auto()  # {
    TOK_RBRACE = auto()  # }

    # Affectation
    TOK_AFFECT = auto()  # =

    # Séparateurs
    TOK_SEMICOLON = auto()  # ;
    TOK_COMMA = auto()  # ,

    # Adresse et valeur
    TOK_ADDRESS = auto()  # &
    TOK_DEREF = auto()  # *

    # Mots-clés
    TOK_INT = auto()  # int
    TOK_VOID = auto()  # void
    TOK_RETURN = auto()  # return
    TOK_IF = auto()  # if
    TOK_ELSE = auto()  # else
    TOK_FOR = auto()  # for
    TOK_DO = auto()  # do
    TOK_WHILE = auto()  # while
    TOK_BREAK = auto()  # break
    TOK_CONTINUE = auto()  # continue

    # Mots-clés supplémentaires
    TOK_DEBUG = auto()  # debug
    TOK_SEND = auto()  # send
    TOK_RECV = auto()  # recv


class Token:     
    def __init__(self, tok_type: TokenType, value: int = None, repr: str = None):
        self.type: TokenType = tok_type
        self.value: int = value
        self.repr: str = repr
