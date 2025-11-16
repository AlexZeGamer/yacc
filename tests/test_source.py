from io import StringIO


def test_source_from_string_len_getitem_and_str(make_source):
    s = make_source("abc\nxyz")
    assert len(s) == 7
    assert s[0] == "a"
    assert str(s) == "abc\nxyz"


def test_pos_to_line_col(make_source):
    s = make_source("ab\ncd\ne")
    # Positions: 0 a, 1 b, 2 \n, 3 c, 4 d, 5 \n, 6 e
    assert s.pos_to_line_col(0) == (1, 1)
    assert s.pos_to_line_col(1) == (1, 2)
    assert s.pos_to_line_col(2) == (1, 3)
    assert s.pos_to_line_col(3) == (2, 1)
    assert s.pos_to_line_col(5) == (2, 3)
    assert s.pos_to_line_col(6) == (3, 1)


def test_source_from_stdin(monkeypatch):
    from yacc.source import Source

    monkeypatch.setattr("sys.stdin", StringIO("hello from stdin"))
    s = Source.from_stdin()
    assert str(s) == "hello from stdin"
    assert s.name == "<stdin>"

