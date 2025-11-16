import pytest

from yacc.token import TokenType
from yacc.lexer import Lexer
from yacc.utils.errors import CompilationError


def test_lexer_number(make_source):
    lx = Lexer(make_source("42"))
    assert lx.T.type == TokenType.TOK_CONST
    assert lx.T.value == 42
    lx.next()
    assert lx.T.type == TokenType.TOK_EOF


def test_lexer_identifier_and_keyword(make_source):
    lx = Lexer(make_source("int x"))
    assert lx.T.type == TokenType.TOK_INT
    assert lx.T.repr == "int"
    lx.next()
    assert lx.T.type == TokenType.TOK_IDENT
    assert lx.T.repr == "x"


@pytest.mark.parametrize(
    "text, tok",
    [
        ("==", TokenType.TOK_EQ),
        ("!=", TokenType.TOK_NOT_EQ),
        (">=", TokenType.TOK_GREATER_EQ),
        ("<=", TokenType.TOK_LOWER_EQ),
        ("++", TokenType.TOK_INC),
        ("--", TokenType.TOK_DEC),
        ("&&", TokenType.TOK_AND),
        ("||", TokenType.TOK_OR),
        ("(", TokenType.TOK_LPARENTHESIS),
        (")", TokenType.TOK_RPARENTHESIS),
        ("+", TokenType.TOK_ADD),
        ("-", TokenType.TOK_SUB),
        ("*", TokenType.TOK_MUL),
        ("/", TokenType.TOK_DIV),
        ("%", TokenType.TOK_MOD),
        ("!", TokenType.TOK_NOT),
        ("=", TokenType.TOK_AFFECT),
        ("&", TokenType.TOK_ADDRESS),
        (";", TokenType.TOK_SEMICOLON),
        (",", TokenType.TOK_COMMA),
    ],
)
def test_lexer_operators_single_and_double(make_source, text, tok):
    lx = Lexer(make_source(text))
    assert lx.T.type == tok


def test_lexer_skips_whitespace_and_comments(make_source):
    code = "  1  // hello\n /* multi line */   2\n"
    lx = Lexer(make_source(code))
    assert lx.T.type == TokenType.TOK_CONST and lx.T.value == 1
    lx.next()
    assert lx.T.type == TokenType.TOK_CONST and lx.T.value == 2
    lx.next()
    assert lx.T.type == TokenType.TOK_EOF


def test_lexer_unterminated_comment_raises(make_source):
    with pytest.raises((SyntaxError, CompilationError)) as ei:
        Lexer(make_source("/* unterminated"))
    msg = str(ei.value)
    assert "Unterminated comment" in msg


def test_lexer_unknown_token(make_source):
    lx = Lexer(make_source("@"))
    assert lx.T.type == TokenType.TOK_UNKNOWN
    assert lx.T.repr == "@"


def test_lexer_check_and_accept(make_source):
    lx = Lexer(make_source("1"))
    # accept the const
    lx.accept(TokenType.TOK_CONST)
    # now at EOF, attempting to accept an IDENT should error
    with pytest.raises((SyntaxError, CompilationError)) as ei:
        lx.accept(TokenType.TOK_IDENT)
    assert 'expected "TokenType.TOK_IDENT"' in str(ei.value)

