from railai.io_utils import read_semicolon_table, write_csv


def test_read_semicolon_table_skips_comments_and_headers(tmp_path):
    route = tmp_path / "seg.csv"
    route.write_text(
        "# comment\n"
        "PRV9_CNT_BGN;PRV9_CNT_END\n"
        "10;20;0;0;0;0;0;1.0;2.0\n"
        "\n"
        "30;40;0;0;0;0;0;2.0;3.0\n"
    )
    rows, line_count = read_semicolon_table(str(route), "PRV9_CNT_BGN")
    assert line_count == 3
    assert len(rows) == 2
    assert rows[0][0] == "10"


def test_write_csv_roundtrip(tmp_path):
    out = tmp_path / "hits.csv"
    write_csv(str(out), ["km", "counter"], [[12.4, 88], [13.1, 91]])
    text = out.read_text()
    assert "km,counter" in text
    assert "12.4,88" in text
